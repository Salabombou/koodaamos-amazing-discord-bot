from asyncio import AbstractEventLoop
import subprocess
import functools
from utility.common.errors import CommandTimeout, FfprobeError

class FfprobeFormat:
    def __init__(self, result : dict) -> None:
        self.filename = result['filename']
        self.nb_streams = int(result['nb_streams'])
        self.nb_programs = int(result['nb_programs'])
        self.format_name = result['format_name'].split(',')
        self.format_long_name = result['format_long_name']
        self.start_time = result['start_time']
        self.duration = result['duration']
        self.size = result['size']
        self.bit_rate = result['bit_rate']
        self.probe_score = int(result['probe_score'])

class Ffprober:
    def __init__(self, loop : AbstractEventLoop) -> None:
        self.loop = loop
    def output_parser(self, output) -> dict:
        output = output.replace('\r', '') # incase you are using windows
        output = output.split('\n')
        result = {}
        for line in output:
            if '=' in line:
                line = line.split('=')
                result[line[0]] = '='.join(line[1:])
        return result


    async def get_format(self, file) -> dict:
        command = f'ffprobe -show_format -pretty -loglevel error "{file}"'
        try:
            pipe = await self.loop.run_in_executor(
                None, functools.partial(
                    subprocess.run,
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
            )
        except Exception as e:
            raise CommandTimeout()
        err = pipe.stderr.decode() 
        if err != '':
            raise FfprobeError(err)
        output = pipe.stdout.decode()
        return self.output_parser(output)