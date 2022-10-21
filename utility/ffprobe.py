from asyncio import AbstractEventLoop
import subprocess
import functools
from utility.common.errors import FfprobeError
import httpx

class FfprobeFormat:
    def __init__(self, **result) -> None:
        for key, value in result.items():
            result[key] = None if value == 'N/A' else value
        self.filename: str = result['filename']
        self.nb_streams = int(result['nb_streams'])
        self.nb_programs = int(result['nb_programs'])
        self.format_name: str = result['format_name'].split(',')
        self.format_long_name: str = result['format_long_name']
        self.start_time: str = result['start_time']
        self.duration: str = result['duration']
        self.size: str = result['size']
        self.bit_rate: str = result['bit_rate']
        self.probe_score: str = int(result['probe_score'])


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
        command = 'ffprobe -show_format -pretty -loglevel error -'

        if isinstance(file, str):
            async with httpx.AsyncClient() as client:
                resp = await client.get(file)
                resp.raise_for_status()
                file = resp.content

        try:
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