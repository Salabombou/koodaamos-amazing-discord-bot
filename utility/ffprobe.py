from asyncio import AbstractEventLoop
import subprocess
import functools
import tempfile
from utility.common.errors import FfprobeError
import concurrent.futures
import httpx
from utility.common import decorators

class FfprobeFormat:
    def __init__(
        self, /,
        filename: str,
        nb_streams: str,
        nb_programs: str,
        format_name: str,
        format_long_name: str,
        start_time: str,
        duration: str,
        size: str,
        bit_rate: str,
        probe_score: str,
        **kwargs
    ) -> None:
        self.filename = filename
        self.nb_streams = int(nb_streams)
        self.nb_programs = int(nb_programs)
        self.format_name = format_name.split(',')
        self.format_long_name: str = format_long_name
        self.start_time = start_time
        self.duration = duration
        self.size = size
        self.bit_rate = bit_rate
        self.probe_score = int(probe_score)
        self.other = kwargs

class Ffprober:
    def __init__(self, loop: AbstractEventLoop) -> None:
        self.loop = loop

    def output_parser(self, output: str) -> dict:
        output = output.replace('\r', '')  # incase you are using windows
        lines = output.split('\n')
        lines = [line.split('=') for line in lines if '=' in line]
        result = {line[0]: '='.join(line[1:]) for line in lines}
        return result
    
    @staticmethod
    def create_size(size: int) -> str:
        character_length = len(str(size))
        if character_length < 4:
            return f'{size} byte'
        if character_length >= 4 and character_length < 7:
            return f'{size / 1000} Kibyte'
        if character_length >= 7:
            return f'{size / (1000_1000)} Mibyte'
        raise FfprobeError('File size could not be determined')

    @decorators.Async.logging.log
    @decorators.Async.ffmpeg.create_dir
    async def get_format(self, file : str | bytes, _dir: str = None) -> dict:
        command = 'ffprobe -show_format -pretty -loglevel error "%s"'

        if isinstance(file, str):
            async with httpx.AsyncClient() as client:
                resp = await client.get(file)
                resp.raise_for_status()
                file = resp.content
        with tempfile.NamedTemporaryFile(delete=False, dir=_dir) as temp: # create a temp file in the temp dir
            try:
                temp.write(file)  # write into the temp file
                temp.flush()  # flush the file
                command = command % temp.name
                    
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    pipe = await self.loop.run_in_executor(
                        pool, functools.partial(
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