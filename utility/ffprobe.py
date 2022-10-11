from asyncio import AbstractEventLoop
import subprocess
import functools
from utility.common.errors import CommandTimeout, FfprobeError
from utility.common import file_management

class FfprobeFormat:
    def __init__(self, **result) -> None:
        for key, value in result.items():
            result[key] = None if value == 'N/A' else value
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

    async def get_format(self, file : str | bytes) -> dict:
        command = 'ffprobe -show_format -pretty -loglevel error '
        is_str = isinstance(file, str)
        if is_str:
            command += f'"{file}"'
        else:
            command += '-'
        try:
            pipe = await self.loop.run_in_executor(
                None, functools.partial(
                    subprocess.run,
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    input=file if not is_str else None,
                    bufsize=10**8,
                    timeout=10
                )
            )
        except:
            print('ffprobe')
            raise CommandTimeout()
        err: bytes = pipe.stderr
        out: bytes = pipe.stdout
        err = err.decode()
        out = out.decode()
        if out == '':
            raise FfprobeError(err)
        return self.output_parser(out)