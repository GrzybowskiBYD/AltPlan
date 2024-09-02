const days = document.querySelectorAll(".day");

for (const sub of substitutions) {
    set_repl(sub[0], sub[1], sub[2], sub[3]);
}

function set_repl(row, column, text, group) {
    const group_obj = days[column].querySelector(`.gr${group}.r${row}`);
    const subject = group_obj.querySelector(".flex-column .subject");
    subject.innerText = text;
    subject.classList.toggle("repl-text");
    group_obj.querySelector(".teacher_classroom").classList.toggle("repl-s");
}