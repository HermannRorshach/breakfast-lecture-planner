let tpl = document.querySelector("#elem1");
let arr = tpl.textContent.slice(1, length-1).split(", ")
arr[1] = Number(arr[1]) - 1 // Индексация месяцев в JS с нуля, а в python с 1
console.log(arr)
let nextFriday17 = new Date(...arr.map((num) => Number(num)));

let tpl_now = document.querySelector("#elem2");
arr = tpl_now.textContent.slice(1, length-1).split(", ")
arr[1] = Number(arr[1]) - 1 // Индексация месяцев в JS с нуля, а в python с 1
console.log(arr)
let currentDate = new Date(...arr.map((num) => Number(num)));

console.log(currentDate);
console.log(nextFriday17);

if (isNaN(currentDate.getTime()) || isNaN(nextFriday17.getTime())) {
    currentDate = 0;
    nextFriday17 = 0;
}

const diffMs = nextFriday17 - currentDate;
let diffSec = diffMs / 1000;

let days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
let hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
let minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
let seconds = Math.floor((diffMs % (1000 * 60)) / 1000);

let circles = document.querySelectorAll("svg circle:last-of-type");
let numbers = document.querySelectorAll("span.number");
for (let i = 0; i < 8; i++) {
    console.log(circles[i])
    console.log(numbers[i].textContent)
}


let radius = 41;
let circumference = 2 * Math.PI * radius;

function timer() {

    function setDays() {
        if (days > 0) {
            days--
        }
        numbers[0].textContent = days;
        numbers[4].textContent = days;
    }

    function setHours() {
        if (hours > 0) {
            hours--
        } else if (hours === 0) {
            hours = 59;
            setDays();
        }
        numbers[1].textContent = hours;
        numbers[5].textContent = hours;
        setDaysProgressIndicator()
        setTimeProgressIndicator("hours")

    }

    function setMinutes() {
        if (minutes > 0) {
            minutes--
        } else if (minutes === 0) {
            minutes = 59;
            setHours();
        }
        numbers[2].textContent = minutes;
        numbers[6].textContent = minutes;
        setTimeProgressIndicator("minutes");
    }

    function setSeconds() {
        console.log("seconds =", seconds);

        function check() {
            if (days > 0 || hours > 0 || minutes > 0) {
                return true
            }
            return false
        }

        function inner() {
            seconds--
            diffSec --
            if (seconds < 0 && check()) {
                seconds = 59;
                setMinutes();
            } else if (seconds < 0 && !check()) {
                clearInterval(timerId);
            }

            if (seconds >= 0) {
                numbers[3].textContent = seconds;
                numbers[7].textContent = seconds;

                setTimeProgressIndicator("seconds");
            }
        }
        let timerId = setInterval(inner, 1000)
    }


    setDaysProgressIndicator()
    for (let unit of ["hours", "minutes", "seconds"]) {
        setTimeProgressIndicator(unit)
    }
    setSeconds();

    numbers[0].textContent = days;
    numbers[4].textContent = days;
    numbers[1].textContent = hours;
    numbers[5].textContent = hours;
    numbers[2].textContent = minutes;
    numbers[6].textContent = minutes;

}

timer()

function setDaysProgressIndicator() {
    let secInDay = 24 * 60 * 60
    let dayDegrees = 360 - (diffSec / (7 * secInDay) * 360); // 360 - (days / 7 * 360);
    console.log("Функция setDaysProgressIndicotor() запущена, значение dayDegrees =", dayDegrees)
    let dayStrokeDasharray = (dayDegrees / 360) * circumference;
    console.log("Значение dayStrokeDasharray =", dayStrokeDasharray)
    circles[0].setAttribute("style", `
        stroke-dasharray: ${dayStrokeDasharray} ${circumference};
        stroke-width: 6;
        `);
    circles[4].setAttribute("style", `
        stroke-dasharray: ${dayStrokeDasharray} ${circumference};
        stroke-width: 6;
        `);
}

function setTimeProgressIndicator(units) {
    let index = {"hours": 0, "minutes": 1, "seconds": 2}[units];
    units = [hours, minutes, seconds][index]
    let degrees = 360 - (units / 60 * 360);
    let strokeDasharray = (degrees / 360) * circumference;
    circles[index + 1].setAttribute("style", `
        stroke-dasharray: ${strokeDasharray} ${circumference};
        stroke-width: 6;
        `);
    circles[index + 5].setAttribute("style", `
        stroke-dasharray: ${strokeDasharray} ${circumference};
        stroke-width: 6;
        `);
}

console.log(`Осталось: ${days} дн, ${hours} ч, ${minutes} мин, ${seconds} сек`);
