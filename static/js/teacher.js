const socket = io();
const roomCode = document.getElementById('roomCode').textContent;
const studentCount = document.getElementById('studentCount');
const sendPollBtn = document.getElementById('sendPollBtn');
const pollResults = document.getElementById('pollResults');
const goodBar = document.getElementById('goodBar');
const neutralBar = document.getElementById('neutralBar');
const badBar = document.getElementById('badBar');
const goodCount = document.getElementById('goodCount');
const neutralCount = document.getElementById('neutralCount');
const badCount = document.getElementById('badCount');

let currentPollId = null;

socket.emit('join', {room: roomCode});

socket.on('update_student_count', (data) => {
    studentCount.textContent = data.count;
});

sendPollBtn.addEventListener('click', () => {
    socket.emit('send_poll', {room: roomCode});
    pollResults.classList.remove('hidden');
    resetResults();
});

socket.on('new_poll', (data) => {
    currentPollId = data.poll_id;
});

socket.on('update_results', (data) => {
    updateResults(data);
});

function resetResults() {
    goodBar.style.width = '0%';
    neutralBar.style.width = '0%';
    badBar.style.width = '0%';
    goodCount.textContent = '0';
    neutralCount.textContent = '0';
    badCount.textContent = '0';
}

function updateResults(data) {
    const total = data.good + data.neutral + data.bad;
    const goodPercentage = total > 0 ? (data.good / total) * 100 : 0;
    const neutralPercentage = total > 0 ? (data.neutral / total) * 100 : 0;
    const badPercentage = total > 0 ? (data.bad / total) * 100 : 0;

    goodBar.style.width = `${goodPercentage}%`;
    neutralBar.style.width = `${neutralPercentage}%`;
    badBar.style.width = `${badPercentage}%`;

    goodCount.textContent = data.good;
    neutralCount.textContent = data.neutral;
    badCount.textContent = data.bad;
}
