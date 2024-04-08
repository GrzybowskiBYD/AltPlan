const r = document.querySelector(':root');
let darkMatchMedia = window.matchMedia("(prefers-color-scheme: dark)");
let dark = darkMatchMedia.matches;
const logo = document.getElementById("logo");

c = document.cookie;
let color_scheme = localStorage.getItem("color_scheme");
let preffered_theme = localStorage.getItem("theme");
let background = localStorage.getItem("background");
const temp_groups = localStorage.getItem("groups");
let footer_warning;
if (localStorage.getItem("warning") === null) {
    footer_warning = true;
}
else {
    footer_warning = Boolean(localStorage.getItem("warning") === "true");
}
let groups;
if (temp_groups) groups = JSON.parse(temp_groups);
else groups = [false, false, false, false, false, false, false, false];

darkMatchMedia.onchange = (e) => {
    if (preffered_theme === "system") {
        dark = e.matches;
        refresh_colors();
    }
}


function logo_click() {
    dark = !dark;
    logo.style.transform += `rotate(360deg)`;
    refresh_colors();
}

function refresh_colors() {
    color_scheme = localStorage.getItem("color_scheme");
    preffered_theme = localStorage.getItem("theme");
    background = localStorage.getItem("background");
    if (preffered_theme === "dark") dark = true;
    else if (preffered_theme === "light") dark = false;
    else dark = darkMatchMedia.matches;
    if (!color_scheme) {
        color_scheme = "rgb(154, 61, 36)"
    }
    if (background) r.style.setProperty("--background", `url(/backgrounds/${background})`);
    if (dark) {
        r.style.setProperty("--main-color", color_scheme);
        r.style.setProperty("--theme-background", "rgb(51, 51, 51)");
        r.style.setProperty("--positive", "rgb(0, 0, 0)");
        r.style.setProperty("--negative", "rgb(255, 255, 255)");
        r.style.setProperty("--theme-wght", 300);
        let meta = document.createElement('meta');
        meta.name = "theme-color";
        meta.content = color_scheme;
        meta.media = "(prefers-color-scheme: dark)";
        document.getElementsByTagName('head')[0].appendChild(meta);
    }
    else {
        r.style.setProperty("--main-color", color_scheme);
        r.style.setProperty("--theme-background", "rgb(250, 250, 250)");
        r.style.setProperty("--positive", "rgb(255, 255, 255)");
        r.style.setProperty("--negative", "rgb(0, 0, 0)");
        r.style.setProperty("--theme-wght", 700);
        let meta = document.createElement('meta');
        meta.name = "theme-color";
        meta.content = color_scheme;
        meta.media = "(prefers-color-scheme: light)";
        document.getElementsByTagName('head')[0].appendChild(meta);
    }
}

refresh_colors();
