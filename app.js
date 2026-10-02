// State Management
let mainWallet = 0;
let playWallet = 10;
let currentStake = 10;
let selectedCartelas = [];
let gameId = 1;
let countdown = 49;
let timerInterval = null;

// Initial Setup
document.addEventListener("DOMContentLoaded", () => {
    generateCartelaGrid();
    startCountdown();
    setupBingoBoard();
});

// Generate 1 to 600 Cartelas
function generateCartelaGrid() {
    const grid = document.getElementById("cartela-grid");
    grid.innerHTML = "";
    for (let i = 1; i <= 600; i++) {
        const box = document.createElement("div");
        box.className = "cartela-box";
        box.innerText = i;
        box.onclick = () => selectCartela(i, box);
        grid.appendChild(box);
    }
}

// Handle Cartela Selection Max 3
function selectCartela(num, element) {
    if (selectedCartelas.includes(num)) {
        selectedCartelas = selectedCartelas.filter(id => id !== num);
        element.classList.remove("selected");
    } else {
        if (selectedCartelas.length >= 3) {
            alert("ቢበዛ መምረጥ የሚችሉት 3 ካርቴላ ብቻ ነው!");
            return;
        }
        selectedCartelas.push(num);
        element.classList.add("selected");
    }
    document.getElementById("selected-count").innerText = selectedCartelas.length;
}

// Tab Switching Navigation
function switchTab(tabName) {
    document.querySelectorAll(".screen").forEach(s => s.classList.add("hidden"));
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    
    if (tabName === 'game') {
        document.getElementById("selection-screen").classList.remove("hidden");
    } else {
        document.getElementById(${tabName}-screen).classList.remove("hidden");
    }
    // Update visual tab activation button
}

// Countdown Logic (49 seconds)
function startCountdown() {
    countdown = 49;
    document.getElementById("countdown").innerText = countdown;
    
    timerInterval = setInterval(() => {
        countdown--;
        document.getElementById("countdown").innerText = countdown;
        
        if (countdown <= 0) {
            clearInterval(timerInterval);
            transitionToBingoGame();
        }
    }, 1000);
}

// Transition Screen when Timer Hits 0
function transitionToBingoGame() {
    document.getElementById("selection-screen").classList.add("hidden");
    document.getElementById("game-screen").classList.remove("hidden");
    
    // Format Game ID to 0001 format
    document.getElementById("game-id").innerText = String(gameId).padStart(4, '0');
    
    renderActiveMatrices();
    startCallingNumbers();
}

// Generate 5x5 Matrix for selected items
function renderActiveMatrices() {
    const container = document.getElementById("active-cartelas-display");
    container.innerHTML = "";
    
    if(selectedCartelas.length === 0) {
        container.innerHTML = "<p style='color:red;'>ምንም ካርቴላ አልመረጡም! እባክዎ ቀጣዩን ጨዋታ ይጠብቁ።</p>";
        return;
    }

    selectedCartelas.forEach(id => {
        const wrap = document.createElement("div");
        wrap.innerHTML = <h4>📋 ካርቴላ #${id}</h4>;
        const matrix = document.createElement("div");
        matrix.className = "matrix-5x5";
        
        // Populate 25 elements mock numbers
        for(let i=0; i<25; i++) {
            const cell = document.createElement("div");
            cell.className = "matrix-cell";
            cell.innerText = Math.floor(Math.random() * 75) + 1;
            matrix.appendChild(cell);
        }
        wrap.appendChild(matrix);
        container.appendChild(wrap);
    });
}

// Initialize Board Columns
function setupBingoBoard() {
    for(let i=1; i<=15; i++) document.getElementById("col-B").innerHTML += <span id="num-${i}">${i}</span>;
    for(let i=16; i<=30; i++) document.getElementById("col-I").innerHTML += <span id="num-${i}">${i}</span>;
	for(let i=31; i<=45; i++) document.getElementById("col-N").innerHTML += <span id="num-${i}">${i}</span>;
    for(let i=46; i<=60; i++) document.getElementById("col-G").innerHTML += <span id="num-${i}">${i}</span>;
    for(let i=61; i<=75; i++) document.getElementById("col-O").innerHTML += <span id="num-${i}">${i}</span>;
}

// Simulation for calling numbers
function startCallingNumbers() {
    let pool = Array.from({length: 75}, (_, i) => i + 1);
    let calledCount = 0;
    
    let callInterval = setInterval(() => {
        if (pool.length === 0 || calledCount >= 15) { // Call 15 numbers as a demo
            clearInterval(callInterval);
            resetToNextGame();
            return;
        }
        
        let randIndex = Math.floor(Math.random() * pool.length);
        let num = pool.splice(randIndex, 1)[0];
        calledCount++;
        
        let letter = "";
        if(num <= 15) letter = "B";
        else if(num <= 30) letter = "I";
        else if(num <= 45) letter = "N";
        else if(num <= 60) letter = "G";
        else letter = "O";
        
        // Show in screen
        document.getElementById("live-ball-screen").innerText = ${letter} - ${num};
        
        // Cross out on structural list board
        let boardNum = document.getElementById(num-${num});
        if(boardNum) boardNum.className = "called-num";
        
    }, 3000); // Calls every 3 seconds
}

function resetToNextGame() {
    setTimeout(() => {
        gameId++;
        selectedCartelas = [];
        document.getElementById("selected-count").innerText = "0";
        document.getElementById("game-screen").classList.add("hidden");
        document.getElementById("selection-screen").classList.remove("hidden");
        
        // Reset Board classes
        document.querySelectorAll(".called-num").forEach(el => el.className = "");
        generateCartelaGrid();
        startCountdown();
    }, 5000);
}