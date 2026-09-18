let selectedCartelas = [];
let timeLeft = 49;
let selectionOpen = true;

// 💥 የእርስዎን ኮምፒውተር አይፒ አድራሻ እዚህ ያስገቡ
const API_BASE_URL = "http://192.168.125.45:5000"; 
const urlParams = new URLSearchParams(window.location.search);
const TelegramUserID = urlParams.get('user_id') || "12345"; 

window.onload = function() {
    createAllCartelas();
    setupBingoBoardNumbers();
    startCountdown(); 
    loadRealBalance();
};

function createAllCartelas() {
    const cartelaList = document.getElementById('cartela-list');
    if (cartelaList) {
        cartelaList.innerHTML = ""; 
        for (let i = 1; i <= 600; i++) {
            let box = document.createElement('div');
            box.className = 'cartela-box';
            box.innerText = i;
            box.onclick = function() { selectCartela(i, box); };
            cartelaList.appendChild(box);
        }
    }
}

function loadRealBalance() {
    fetch(${API_BASE_URL}/api/get_balance?user_id=${TelegramUserID})
        .then(res => res.json())
        .then(data => {
            const mainW = document.getElementById('main-wallet-amount');
            const playW = document.getElementById('play-wallet-amount');
            if (mainW) mainW.innerText = data.main_wallet.toFixed(2) + " ብር";
            if (playW) playW.innerText = data.play_wallet.toFixed(2) + " ብር";
        }).catch(err => console.log(err));
}

function buyCartelaOnDatabase() {
    fetch(${API_BASE_URL}/api/buy_cartela, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: TelegramUserID })
    })
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            document.getElementById('main-wallet-amount').innerText = data.main_wallet.toFixed(2) + " ብር";
            document.getElementById('play-wallet-amount').innerText = data.play_wallet.toFixed(2) + " ብር";
        } else {
            alert(data.message);
        }
    }).catch(err => console.log(err));
}

function selectCartela(id, element) {
    if (!selectionOpen) return;
    if (selectedCartelas.includes(id)) {
        selectedCartelas = selectedCartelas.filter(item => item !== id);
        element.classList.remove('selected');
    } else {
        if (selectedCartelas.length >= 5) {
            alert("መምረጥ የሚችሉት እስከ 5 ካርቴላ ብቻ ነው!");
            return;
        }
        buyCartelaOnDatabase(); // 💥 ካርቴላ ሲመረጥ ብር ይቀንሳል
        selectedCartelas.push(id);
        element.classList.add('selected');
        generate5x5Grid(); 
    }
}

function generate5x5Grid() {
    const grid = document.getElementById('bingo-grid');
    if (document.getElementById('selected-cartela-display')) document.getElementById('selected-cartela-display').classList.remove('hidden');
    if (grid) {
        grid.innerHTML = '';
        for (let i = 1; i <= 25; i++) {
            let cell = document.createElement('div');
            cell.className = 'grid-cell';
            cell.innerText = i === 13 ? "FREE" : Math.floor(Math.random() * 75) + 1;
            grid.appendChild(cell);
        }
    }
}

function startCountdown() {
    const timerElement = document.getElementById('timer');
    const timerInterval = setInterval(function() {
        timeLeft--;
        if (timerElement) timerElement.innerText = timeLeft;
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            selectionOpen = false;
            document.getElementById('timer-box').innerText = "ምርጫ ተዘግቷል! ጨዋታው ተጀምሯል...";
            document.getElementById('cartela-list').classList.add('hidden');
            document.getElementById('select-title').classList.add('hidden');
            document.getElementById('bingo-board').classList.remove('hidden');
            startBingoCalling(); 
        }
    }, 1000);
}

function setupBingoBoardNumbers() {
	const columns = {'B': {s:1, e:15, id:'col-B'}, 'I': {s:16, e:30, id:'col-I'}, 'N': {s:31, e:45, id:'col-N'}, 'G': {s:46, e:60, id:'col-G'}, 'O': {s:61, e:75, id:'col-O'}};
    for (let key in columns) {
        let col = columns[key];
        let el = document.getElementById(col.id);
        if (el) {
            el.innerHTML = "";
            for (let n = col.s; n <= col.e; n++) {
                let numSpan = document.createElement('div');
                numSpan.className = 'board-num';
                numSpan.id = 'b-num-' + n;
                numSpan.innerText = n;
                el.appendChild(numSpan);
            }
        }
    }
}

function speakBingo(text) {
    if ('speechSynthesis' in window) {
        let utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US'; utterance.rate = 0.9;
        let voices = window.speechSynthesis.getVoices();
        let femaleVoice = voices.find(v => v.name.includes('Google US English')  v.name.includes('Zira')  v.name.includes('Female'));
        if (femaleVoice) utterance.voice = femaleVoice;
        window.speechSynthesis.speak(utterance);
    }
}

function startBingoCalling() {
    let allNumbers = [];
    for (let i = 1; i <= 75; i++) allNumbers.push(i);
    allNumbers.sort(() => Math.random() - 0.5);
    let currentIndex = 0;
    const callingInterval = setInterval(function() {
        if (currentIndex >= allNumbers.length) { clearInterval(callingInterval); return; }
        let num = allNumbers[currentIndex];
        let letter = num<=15?"B":num<=30?"I":num<=45?"N":num<=60?"G":"O";
        document.getElementById('called-number').innerText = letter + "-" + num;
        speakBingo(letter + " " + num);
        const target = document.getElementById('b-num-' + num);
        if (target) target.classList.add('highlighted');
        currentIndex++;
    }, 4000); 
}

function switchTab(tabName) {
    ['game', 'wallet', 'history', 'profile'].forEach(t => {
        document.getElementById(t + '-tab').classList.add('hidden');
        document.getElementById('nav-' + t).classList.remove('active');
    });
    document.getElementById(tabName + '-tab').classList.remove('hidden');
    document.getElementById('nav-' + tabName).classList.add('active');
}