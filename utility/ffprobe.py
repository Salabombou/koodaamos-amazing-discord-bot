from asyncio import AbstractEventLoop
import subprocess
import functools
import tempfile
from utility.common.errors import FfprobeError
import httpx

class FfprobeFormat:
    def __init__(
        self,
        filename,
        nb_streams,
        nb_programs,
        format_name,
        format_long_name,
        start_time,
        duration,
        size,
        bit_rate,
        probe_score
    ) -> None:
        self.filename: str = filename
        self.nb_streams = int(nb_streams)
        self.nb_programs = int(nb_programs)
        self.format_name: str = format_name.split(',')
        self.format_long_name: str = format_long_name
        self.start_time: str = start_time
        self.duration: str = duration
        self.size: str = size
        self.bit_rate: str = bit_rate
        self.probe_score: str = int(probe_score)

class Ffprober:
    def __init__(self, loop: AbstractEventLoop) -> None:
        self.loop = loop

    def output_parser(self, output) -> dict:
        output = output.replace('\r', '')  # incase you are using windows
        output = output.split('\n')
        result = {}
        for line in output:
            if '=' in line:
                line = line.split('=')
                result[line[0]] = '='.join(line[1:])
        return result
    
    @staticmethod
    def create_size(size: int) -> str:
        character_length = len(str(size))
        if character_length < 4:
            return f'{size} byte'
        if character_length >= 4 and character_length < 7:
            return f'{size / 1000} Kibyte'
        if character_length >= 7:
            return f'{size / (1000*1000)} Mibyte'
        raise FfprobeError('File size could not be determined')

    async def get_format(self, file : str | bytes) -> dict:
        command = 'ffprobe -show_format -pretty -loglevel error "%s"'

        if isinstance(file, str):
            async with httpx.AsyncClient() as client:
                resp = await client.get(file)
                resp.raise_for_status()
                file = resp.content
        
        with tempfile.TemporaryDirectory() as dir:  # create a temp dir, deletes itself and its content after use
            with tempfile.NamedTemporaryFile(delete=False, dir=dir) as temp: # create a temp file in the temp dir
                try:
                    temp.write(file)  # write into the temp file
                    temp.flush()  # flush the file
                    command = command % temp.name
                    
                    pipe = await self.loop.run_in_executor(
                        None, functools.partial(
                            subprocess.run,
                            command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            input=file,
                            bufsize=10**8,
                            timeout=20
                        )
                    )
                except FfprobeError:
                    raise FfprobeError('Command timeout')
        err: bytes = pipe.stderr
        out: bytes = pipe.stdout
        err = err.decode()
        out = out.decode()
        if out == '':
            raise FfprobeError(err)
        parsed = self.output_parser(out)
        parsed['size'] = self.create_size(len(file))
        return parsed