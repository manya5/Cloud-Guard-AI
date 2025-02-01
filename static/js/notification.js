let toggleBtn1 = document.querySelector('.toggle-btn1')
let toggleCircle1 = document.querySelector('.toggle-circle1')
let toggle1 = 0;
toggleBtn1.addEventListener('click', () => {
    toggle1 = !toggle1;
    if(toggle1){
        toggleCircle1.classList.remove('left-1')
        toggleCircle1.style.right = '0.25rem'
        toggleBtn1.classList.add('bg-blue-600')
    }else{
        toggleCircle1.classList.add('left-1')
        toggleCircle1.style.right = '0.25rem'
        toggleBtn1.classList.remove('bg-blue-600')
    }
})

let toggleBtn2 = document.querySelector('.toggle-btn2')
let toggleCircle2 = document.querySelector('.toggle-circle2')
let toggle2 = 0;
toggleBtn2.addEventListener('click', () => {
    toggle2 = !toggle2;
    if(toggle2){
        toggleCircle2.classList.remove('left-1')
        toggleCircle2.style.right = '0.25rem'
        toggleBtn2.classList.add('bg-blue-600')
    }else{
        toggleCircle2.classList.add('left-1')
        toggleCircle2.style.right = '0.25rem'
        toggleBtn2.classList.remove('bg-blue-600')
    }
})

