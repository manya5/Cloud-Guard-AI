let sendBtn = document.getElementById('sendData')

const ctx = document.getElementById('myChart');

new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
    datasets: [{
      label: '# of Votes',
      data: [12, 19, 3, 5, 2, 3],
      borderWidth: 1
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});



let profileEditBtn = document.querySelector('.profile-edit-btn')
let profileCancelBtn = document.querySelector('.profile-cancel-btn')
let editProfile = document.querySelector('.edit-profile')

profileEditBtn.addEventListener('click', () => {
    editProfile.classList.remove('hidden')
})

profileCancelBtn.addEventListener('click', () => {
    editProfile.classList.add('hidden')
})



