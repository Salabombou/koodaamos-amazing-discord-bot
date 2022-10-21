class CommandTimeout(Exception):
    def __init__(self) -> None:
        self.message = 'Command timeout'

    def __str__(self) -> str:
        return self.message


class SauceNotFound(Exception):
    def __init__(self) -> None:
        self.message = 'Could not find the sauce...'

    def __str__(self) -> str:
        return self.message


class SongNotFound(Exception):
    def __init__(self) -> None:
        self.message = 'No songs found at that number'

    def __str__(self) -> str:
        return self.message


class UrlInvalid(Exception):
    def __init__(self) -> None:
        self.message = 'Invalid url'

    def __str__(self) -> str:
        return self.message


class VideoUnavailable(Exception):
    def __init__(self) -> None:
        self.message = 'Video not available'

    def __str__(self) -> str:
        return self.message


class VideoTooLong(Exception):
    def __init__(self, seconds=None) -> None:
        max_duration = f'Maximum length of the video is {seconds} seconds.' if seconds != None else ''
        self.message = 'Video is too long to be downloaded. ' + max_duration

    def __str__(self) -> str:
        return self.message


class UnsupportedUrl(Exception):
    def __init__(self) -> None:
        self.message = 'Url not supported'

    def __str__(self) -> str:
        return self.message


class DownloadFailure(Exception):
    def __init__(self) -> None:
        self.message = 'File could not be downloaded'

    def __str__(self) -> str:
        return self.message


class TargetNotFound(Exception):
    def __init__(self) -> None:
        self.message = 'No images/videos in the reply or video or audio is not accepted'

    def __str__(self) -> str:
        return self.message


class FfmpegError(Exception):
    def __init__(self, error) -> None:
        self.message = error

    def __str__(self) -> str:
        return self.message


class FfprobeError(Exception):
    def __init__(self, error) -> None:
        self.message = error

    def __str__(self) -> str:
        return self.message


class VideoSearchNotFound(Exception):
    def __init__(self, query) -> None:
        self.message = f'No videos were found with the query "{query}"'

    def __str__(self) -> str:
        return self.message


class PomfUploadFail(Exception):
    def __init__(self) -> None:
        self.message = 'Failed to upload the file to pomf.cat'

    def __str__(self) -> str:
        return self.message


class TargetError(Exception):
    def __init__(self, message) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class UrlRedirectError(Exception):
    def __init__(self, message) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class NaughtyError(Exception):
    def __init__(self) -> None:
        pass
