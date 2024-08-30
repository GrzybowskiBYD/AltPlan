const weekday_span = document.getElementById("weekday-span");
const weekdays = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek"];

r.style.setProperty("--day-move", `-${weekday * 100}vw`)

weekday_span.innerText = weekdays[weekday];
function prev_day() {
    if (weekday > 0) {
        weekday -= 1;
    }
    r.style.setProperty("--day-move", `-${weekday * 100}vw`)
    weekday_span.innerText = weekdays[weekday];
}

function next_day() {
    if (weekday < 4) {
        weekday += 1;
    }
    r.style.setProperty("--day-move", `-${weekday * 100}vw`)
    weekday_span.innerText = weekdays[weekday];
}