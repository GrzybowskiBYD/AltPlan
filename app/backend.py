import os.path
import shutil
import threading
import hashlib

import datetime
import time
import urllib.request

import pytz

from URLNormalize import UrlObj

import bs4
import re


class Backend:
    def __init__(self):
        self.change_date = datetime.datetime.now(pytz.timezone('Europe/Warsaw'))
        self.nav_list = {"classes": {}, "teachers": {}, "classrooms": {}}
        self.weekdays = ["poniedziałek", "wtorek", "środa", "czwartek", "piątek"]
        self.weekday = -1
        self.date = datetime.datetime

        self.info = ""

        self.zse_url = "https://plan.zse.bydgoszcz.pl"
        self.subs_url = "https://zastepstwa.zse.bydgoszcz.pl/"
        # self.subs_url = "http://localhost/"
        self.hash_url = "https://zastepstwa.zse.bydgoszcz.pl/"
        # self.hash_url = "http://localhost/"

        self.class_cache = {}
        self.teacher_cache = {}
        self.teacher_subs_list = {}
        self.substitutions_html = ""

        self.refresh()
        self.subs_hash_old = self.subs_hash

    def heartbeat(self):
        temp_hash = self.subs_hash
        if temp_hash != self.subs_hash_old:
            print("changed!")
            self.change_date = datetime.datetime.now(pytz.timezone('Europe/Warsaw'))
            self.subs_hash_old = temp_hash
            self.refresh()

    @property
    def subs_hash(self):
        r = urllib.request.urlopen(self.hash_url)
        return hashlib.sha224(r.read()).hexdigest()

    def refresh(self):
        self.nav_list = {"classes": {}, "teachers": {}, "classrooms": {}}
        r = urllib.request.urlopen(self.subs_url)
        self.substitutions_html = bs4.BeautifulSoup(r, "html.parser")
        self.date = datetime.datetime.strptime(
            re.search(r"(\d\d.\d\d.\d\d\d\d)", self.substitutions_html.text).group(1), "%d.%m.%Y")

        self.info = ""

        self.__cache_list()
        self.__cache_weekday()
        self.class_cache = {}
        self.__cache_teacher_subs_list()

    def url_to_name(self, url):
        url = self.url_obj(url).id
        g = re.search(r"([ons])", url).group(1)
        return self.nav_list[{"o": "classes", "n": "teachers", "s": "classrooms"}[g]][
            url]

    def __cache_list(self):
        r = urllib.request.urlopen(f"{self.zse_url}/lista.html")
        bs = bs4.BeautifulSoup(r, "html.parser")
        for i in range(3):
            for x in bs.find_all("ul")[i].find_all("li"):
                split = x.a.text.split(" ")
                url = self.url_obj(x.a["href"]).id
                if i == 0:
                    name = split[0] + (f" {split[-1]}" if len(split) > 1 else "")
                    self.nav_list[list(self.nav_list.keys())[i]].update({url: name})
                elif i == 2:
                    self.nav_list[list(self.nav_list.keys())[i]].update({url: split[0]})
                else:
                    self.nav_list[list(self.nav_list.keys())[i]].update({url: x.a.text})

    def __cache_weekday(self):
        self.weekday = -1
        r = urllib.request.urlopen(self.subs_url)
        bs = bs4.BeautifulSoup(r, "html.parser")
        regex = re.findall(r"\d\d.\d\d.\d\d\d\d", bs.find("nobr").text)
        if not regex:
            print(f"WARNING! Date not found, setting to 0 ({self.weekdays[0]})")
            self.weekday = 0
            return
        first = datetime.datetime.strptime(regex[0], "%d.%m.%Y")
        last = datetime.datetime.strptime(regex[-1], "%d.%m.%Y")
        now = datetime.datetime.now(pytz.timezone('Europe/Warsaw'))
        self.weekday = clamp_datetime(now, first, last).weekday()

    def get_class_subs(self, url):
        url = self.url_obj(url).id
        if url not in self.nav_list["classes"]:
            return []
        class_name = self.nav_list["classes"][url]
        bs = self.substitutions_html
        trs = bs.find_all("tr")
        class_name = class_name.split(" ")[0]
        class_name = f"{class_name[0]} {class_name[1:]}"
        results = []
        current_teacher = None
        for tr in trs:
            tds = tr.find_all("td")
            texts = [td.text.strip() for td in tds]
            if len(texts) < 4:
                current_teacher = tr.text.strip()
                continue
            if "opis" in texts or not "".join(texts):
                continue
            regex = re.search(class_name + r"(?:\((\d)\))?(?: - (.*))?", texts[1])
            if regex:
                group = regex.group(1)
                nr = int(tds[0].text)

                regex_date = re.search(r"(\d?\d.\d?\d.)(\d\d)?(\d\d)", current_teacher)
                # date in format DD.MM.YYYY present in the substitution name field
                if regex_date:
                    normalized_date = regex_date[0] if regex_date.group(2) else f"{regex_date.group(1)}{datetime.datetime.now().year//100}{regex_date.group(3)}"
                    weekday = datetime.datetime.strptime(normalized_date, "%d.%m.%Y").weekday()
                # not present, default to global weekday value
                else:
                    weekday = self.weekday

                teacher = texts[2] if texts[2] else ""
                comments = texts[3] if texts[3] else ""
                classroom = regex.group(2) if regex.group(2) else ""

                info = f"{teacher} {f"({comments}) " if comments else ""}{classroom}".strip()

                group_nr = int(group) if group else 0

                results.append((nr, weekday, info, group_nr))
        return results

    def get_teacher_subs(self, url: UrlObj):
        if url not in self.nav_list.values():
            return []
        teacher_name = self.nav_list["teachers"][url]
        r = re.search(r"(.)\.([^(\s]*)", teacher_name)
        if " ".join(r.groups()) in self.teacher_subs_list.keys():
            return self.teacher_subs_list[" ".join(r.groups())]
        return []

    def __cache_teacher_subs_list(self):
        bs = self.substitutions_html
        trs = bs.find_all("tr")
        results = {}
        teacher_results = []
        append_flag = False
        teacher = ""
        teacher_raw = ""
        for tr in trs[1:]:
            tds = tr.find_all("td")
            texts = [td.text.strip() for td in tds]
            if len(texts) < 4:
                if append_flag:
                    if teacher in results.keys():
                        results[teacher].append(texts)
                    else:
                        results.update({teacher: teacher_results})
                teacher_raw = tr.text.strip()
                teacher = re.search(r"(^.).* (.*)", teacher_raw)
                if teacher:
                    teacher = " ".join(teacher.groups())
                teacher_results = []
                append_flag = True
                continue
            if "opis" in texts or not "".join(texts):
                continue
            nr = int(tds[0].text)
            regex_date = re.search(r"(\d?\d.\d?\d.)(\d\d)?(\d\d)", teacher_raw)
            # date in format DD.MM.YYYY present in the substitution name field
            if regex_date:
                normalized_date = regex_date[0] if regex_date.group(
                    2) else f"{regex_date.group(1)}{datetime.datetime.now().year // 100}{regex_date.group(3)}"
                weekday = datetime.datetime.strptime(normalized_date, "%d.%m.%Y").weekday()
            # not present, default to global weekday value
            else:
                weekday = self.weekday

            regex = re.search(r" - (.*)", texts[1])

            subs_teacher = texts[2] if texts[2] else ""
            comments = texts[3] if texts[3] else ""
            classroom = regex.group(1) if regex.group(1) else ""

            info = f"{subs_teacher} {f"({comments}) " if comments else ""}{classroom}".strip()

            group_nr = -1
            teacher_results.append((nr, weekday, info, group_nr))
            if subs_teacher.strip():
                key = " ".join(re.search(r"^(.).* (.*)", subs_teacher).groups())
                value = (nr, weekday, info, group_nr)
                if key in results.keys():
                    results[key].append(value)
                else:
                    results.update({key: [value]})
        self.teacher_subs_list = results
        return results

    def get_html_subs(self):
        bs = self.substitutions_html
        trs = bs.find_all("tr")
        text = trs[0].text
        key = None
        temp = []
        results = {}
        for tr in trs:
            tds = [c for c in tr.children if isinstance(c, bs4.element.Tag)]
            if "st1" in tds[0]["class"]:
                if key is not None:
                    results.update({key: temp})
                key = tds[0].text.strip()
                temp = []
                continue
            if tr.text.strip() != "":
                temp.append([td.text.strip() for td in tds])
        if key is not None:
            results.update({key: temp})
        return text.strip().split("\n"), results

    def get_class_timetable(self, url):
        url = self.url_obj(url).id
        if url in self.class_cache.keys():
            return self.class_cache[url]
        self.__cache_class_timetable(url)
        return self.class_cache[url]

    def __cache_class_timetable(self, url):
        r = urllib.request.urlopen(self.url_obj(url).url)
        bs = bs4.BeautifulSoup(r, "html.parser")
        table = bs.find('table', attrs={'class': 'tabela'})
        tds = table.find_all("td")
        tt = []
        row = []
        temp_wf = {}
        for i, x in enumerate(tds):
            if i % 7 == 0 and i != 0:
                tt.append(row)
                row = []
            if x["class"][0] != 'l':
                row.append([class_obj(x.text.replace(" ", "0"))])
                continue
            if x.text == "\xa0":
                row.append([class_obj()])
                continue
            else:
                groups = [bs4.BeautifulSoup(y.strip(), "html.parser") for y in
                          (str(x.encode_contents(), "utf-8").split("<br/>")) if y != ""]
            final_groups = []
            for group in groups:
                if not group.text:
                    continue

                subject = group.find(attrs={"class": "p"})
                teacher = group.find(attrs={"class": "n"})
                classroom = group.find(attrs={"class": "s"})
                class_tag = group.find(attrs={"class": "o"})

                name = subject.text if subject is not None else group.text
                if teacher is None:
                    t_name = None
                    t_url = None
                else:
                    t_name = teacher.text
                    t_url = re.sub(r".html", "", teacher["href"]) if teacher.has_attr("href") else None
                if classroom is None:
                    c_name = None
                    c_url = None
                else:
                    c_name = classroom.text
                    c_url = re.sub(r".html", "", classroom["href"]) if classroom.has_attr("href") else None
                if class_tag is None:
                    ct_name = None
                    ct_url = None
                else:
                    ct_name = class_tag.text
                    ct_url = re.sub(r".html", "", class_tag["href"]) if class_tag.has_attr("href") else None
                result = re.split(r"-(\d)/(\d)", name)
                name = re.sub(r"-.\d", "", name)
                if "wf" in name:
                    if t_name is None:
                        teacher = self.get_sport_teacher(c_url, i)
                        if teacher:
                            t_name = teacher.text
                            t_url = re.sub(r".html", "", teacher["href"]) if teacher.has_attr("href") else None
                    if t_url not in temp_wf.keys():
                        temp_wf.update({t_url: (max(temp_wf.values()) if temp_wf else 0) + 1})
                    group_nr = temp_wf[t_url]
                    group_count = "wf"
                elif "religia" in name:
                    group_nr = 1
                    group_count = "r"
                else:
                    group_nr = result[1] if len(result) > 1 else 0
                    group_count = result[2] if len(result) > 1 else 0
                obj = class_obj(name, t_name, t_url, c_name, c_url, group_nr, ct_name, ct_url, group_count)
                final_groups.append(obj)
            row.append(final_groups)
        tt.append(row)
        if not self.info:
            raw_text = bs.find(attrs={"align": "left"}).text.strip()
            dates = re.findall(r"\d\d.\d\d.\d\d\d\d", raw_text)
            details = raw_text[raw_text.find("-") + 1:].strip().capitalize() if raw_text.find("-") != -1 else ""
            generated = bs.select('td[align="right"]:not(.op)')[0].text.split()[1]
            self.info = [dates, details, generated]
        self.class_cache.update({self.url_obj(url).id: tt})

    def get_lucky_number(self):
        if os.path.exists("conf/lucky_numbers.txt"):
            with open("conf/lucky_numbers.txt") as f:
                for line in f:
                    obj = line.strip().split(" ")
                    date_obj = datetime.datetime.strptime(obj[0].strip(), "%d.%m.%Y")
                    if date_obj == self.date:
                        return ",".join(obj[1:])
                return "Brak"
        return "Brak"

    def teachers_table(self):
        final = []
        teacher = ""
        for u in self.nav_list["classes"].keys():
            p = self.get_class_timetable(u)
            while len(p) > len(final):
                temp = p[len(final)][0:2]
                [temp.append([]) for _ in range(5)]
                final.append(temp)
            for i, row in enumerate(p):
                for j, day in enumerate(row[2:]):
                    if day[0]["name"] is None:
                        pass
                    elif "z wych" in day[0]["name"]:
                        final[i][j + 2].append(class_obj(tn=day[0]["teacher"]["name"], tu=day[0]["teacher"]["url"],
                                                         ctn=self.nav_list["classes"][u].split(" ")[0],
                                                         ctu=self.url_obj(u).id,
                                                         cn=day[0]["classroom"]["name"], cu=day[0]["classroom"]["url"]))
                        teacher = day[0]["teacher"]["name"]
                        break
                    if not final[i][j + 2]:
                        final[i][j + 2] = []
            for i, row in enumerate(p):
                for j, day in enumerate(row[2:]):
                    if day[0]["name"] is None:
                        pass
                    elif teacher == day[0]["teacher"]["name"] and "z wych" not in day[0]["name"]:
                        final[i][j + 2].append(class_obj(tn=day[0]["teacher"]["name"], tu=day[0]["teacher"]["url"],
                                                         ctn=self.nav_list["classes"][u].split(" ")[0],
                                                         ctu=self.url_obj(u).id,
                                                         cn=day[0]["classroom"]["name"],
                                                         cu=day[0]["classroom"]["url"]))
                        break
                    if not final[i][j + 2]:
                        final[i][j + 2] = []
        return final

    def url_obj(self, url):
        return UrlObj(url, self.zse_url)

    def get_sport_teacher(self, url, td_num, tag="n"):
        r = urllib.request.urlopen(self.url_obj(url).url)
        bs = bs4.BeautifulSoup(r, "html.parser")
        table = bs.find('table', attrs={'class': 'tabela'})
        tds = table.find_all("td")
        return tds[td_num].find(attrs={"class": tag})


def class_obj(name=None, tn=None, tu=None, cn=None, cu=None, group=None, ctn=None, ctu=None, group_count=None):
    obj = {
        "name": name,
        "teacher": {
            "name": tn,
            "url": tu
        },
        "classroom": {
            "name": cn,
            "url": cu
        },
        "class": {
            "name": ctn,
            "url": ctu
        },
        "group": str(group),
        "group-count": str(group_count)
    }
    return obj


def get_themes():
    if not os.path.exists("/app/conf/themes.txt"):
        return ["#9a3d24", "#4abfec", "#643caf", "#4db234", "#c5a217"]
    return [code.strip() for code in open("conf/themes.txt", "r").readlines()]


def clamp_datetime(value, start, end, tz=pytz.timezone("Europe/Warsaw")):
    return clamp(value.replace(tzinfo=tz), start.replace(tzinfo=tz), end.replace(tzinfo=tz))


def clamp(value, start, end):
    if end < value:
        return end
    if value < start:
        return start
    return value


if __name__ == "__main__":
    zs = Backend()
