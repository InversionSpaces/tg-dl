import aiohttp
import imghdr
import aiofiles
import urllib.parse


class ImageDownloadError(Exception):
    pass


class ImageDownloader:
    def __init__(self, chunk_size=1048576, max_size=10485760):
        self.http = aiohttp.ClientSession()
        self.chunk_size = chunk_size
        self.max_size = max_size

    def __aenter__(self):
        return self.http.__aenter__()

    def __aexit__(self, *args):
        return self.http.__aexit__(*args)

    def check_headers(self, response):
        if response.status != 200:
            raise ImageDownloadError(f'HTTP status {response.status}')

        if not (response.content_type.startswith('image')
                or response.content_type.startswith('binary')):
            raise ImageDownloadError(
                f'Content type {response.content_type} is not an image'
            )

        if response.content_length > self.max_size:
            raise ImageDownloadError(
                f'Image size {response.content_length} is too big'
            )

    async def download_image(self, url):
        # Hack to fix URLs without scheme
        url = urllib.parse.urlparse(url, scheme='http').geturl()

        header = await self.http.head(url)
        self.check_headers(header)

        async with self.http.get(url) as response:
            self.check_headers(response)

            async with aiofiles.tempfile.NamedTemporaryFile('wb+', delete=False) as image:
                async for chunk in response.content.iter_chunked(self.chunk_size):
                    await image.write(chunk)

                name = image.name

        type = imghdr.what(name)

        if type is None:
            raise ImageDownloadError('Downloaded file is not an image')

        return (name, type)
