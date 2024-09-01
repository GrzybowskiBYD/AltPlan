const weekday_span = document.getElementById("weekday-span");
const weekdays = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek"];

r.style.setProperty("--day-move", `-${weekday * 100}vw`)

weekday_span.innerText = weekdays[weekday];

function refresh_buttons() {
    if (weekday === 0) {
        document.getElementById("previous-weekday").style.setProperty("color", "#fff8")
    }
    else if (weekday === 4) {
        document.getElementById("next-weekday").style.setProperty("color", "#fff8")
    }
}

function prev_day() {
    document.getElementById("next-weekday").style.setProperty("color", "#fff")
    if (weekday > 0) {
        weekday -= 1;
    }
    refresh_buttons();

    r.style.setProperty("--day-move", `-${weekday * 100}vw`)
    weekday_span.innerText = weekdays[weekday];
}

function next_day() {
    document.getElementById("previous-weekday").style.setProperty("color", "#fff")
    if (weekday < 4) {
        weekday += 1;
    }
    refresh_buttons();

    r.style.setProperty("--day-move", `-${weekday * 100}vw`)
    weekday_span.innerText = weekdays[weekday];
}

refresh_buttons();