let head = document.getElementsByTagName('HEAD')[0];
let link = document.createElement('link');

link.rel = 'stylesheet';
link.type = 'text/css';
link.href = '/static/CSS/transition.css';

head.appendChild(link);