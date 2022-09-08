from requests_toolbelt import MultipartEncoder

fields = {
    'url': 'https://m.media-amazon.com/images/I/51G22XSlZDL._AC_SX569_.jpg'
}
data = MultipartEncoder(fields=fields)
print(data.to_string())