const socket = io();
const roomCode = document.getElementById('roomCode').textContent;
const waitingMessage = document.getElementById('waitingMessage');
const pollOptions = document.getElementById('pollOptions');
const thankYouMessage = document.getElementById('thankYouMessage');
const goodBtn = document.getElementById('goodBtn');
const neutralBtn = document.getElementById('neutralBtn');
const badBtn = document.getElementById('badBtn');

let currentPollId = null;

socket.emit('join', {room: roomCode});

socket.on('new_poll', (data) => {
    currentPollId = data.poll_id;
    showPollOptions();
});

function showPollOptions() {
    waitingMessage.classList.add('hidden');
    pollOptions.classList.remove('hidden');
    thankYouMessage.classList.add('hidden');
}

function hidePollOptions() {
    pollOptions.classList.add('hidden');
    thankYouMessage.classList.remove('hidden');
    setTimeout(() => {
        thankYouMessage.classList.add('hidden');
        waitingMessage.classList.remove('hidden');
    }, 3000);
}

function submitAnswer(answer) {
    if (currentPollId) {
        socket.emit('submit_answer', {poll_id: currentPollId, answer: answer});
        hidePollOptions();
        currentPollId = null;
    }
}

goodBtn.addEventListener('click', () => submitAnswer('good'));
neutralBtn.addEventListener('click', () => submitAnswer('50/50'));
badBtn.addEventListener('click', () => submitAnswer('bad'));

window.addEventListener('beforeunload', () => {
    socket.emit('leave', {room: roomCode});
});
