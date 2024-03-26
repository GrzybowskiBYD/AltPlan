import re


class UrlObj(str):
    def __init__(self, url, url_prefix="https://plan.zse.bydgoszcz.pl"):
        self.url_prefix = url_prefix
        self.url = self.__normalize_url(url)

    @property
    def id(self):
        return re.search(r"plany/(.*)\.html", self.url).group(1)

    def __normalize_url(self, url):
        if self.url_prefix in url:
            if ".html" in url:
                return url
            else:
                return url + ".html"
        else:
            if "plany" in url:
                if ".html" in url:
                    return f"{self.url_prefix}/{url}"
                else:
                    return f"{self.url_prefix}/{url}.html"
            else:
                if ".html" in url:
                    return f"{self.url_prefix}/plany/{url}"
                else:
                    return f"{self.url_prefix}/plany/{url}.html"

    def __str__(self):
        return self.url


if __name__ == "__main__":
    u = UrlObj("o22")
    print(u)
    print(u.id)
