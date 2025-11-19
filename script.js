// 전산세무2급 기출문제 풀이 시스템
// quiz_all_data.js 파일에서 데이터 로드

let currentQuestion = 0;
let score = 0;
let selectedAnswer = null;
let isAnswered = false;
let answersRecord = []; // 각 문제의 답안 기록
let currentRound = 112; // 현재 선택된 회차

// 커스텀 모달 표시
function showModal(title, message, onConfirm, isAlert = false) {
    const modal = document.getElementById('custom-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const cancelBtn = document.getElementById('modal-cancel');
    const confirmBtn = document.getElementById('modal-confirm');
    
    modalTitle.textContent = title;
    modalMessage.textContent = message;
    
    // alert 모드면 취소 버튼 숨김
    if (isAlert) {
        cancelBtn.style.display = 'none';
        confirmBtn.textContent = '확인';
    } else {
        cancelBtn.style.display = 'inline-block';
        confirmBtn.textContent = '확인';
    }
    
    modal.style.display = 'flex';
    
    // 확인 버튼 클릭
    confirmBtn.onclick = () => {
        modal.style.display = 'none';
        if (onConfirm) onConfirm();
    };
    
    // 취소 버튼 클릭
    cancelBtn.onclick = () => {
        modal.style.display = 'none';
    };
    
    // 모달 외부 클릭 시 닫기
    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    };
}

// 회차 선택 함수
function selectRound(round) {
    currentRound = round;
    
    // roundData 객체에 해당 회차가 있는지 확인
    if (!roundData[round]) {
        alert(`${round}회 데이터가 아직 준비되지 않았습니다.`);
        return;
    }
    
    // 모바일 메뉴 닫기
    const sidebar = document.getElementById('sidebar');
    const overlay = document.querySelector('.mobile-overlay');
    if (sidebar && sidebar.classList.contains('active')) {
        sidebar.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
    }
    
    // 문제풀이 섹션으로 이동
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById('quiz-section').classList.add('active');
    
    // 메뉴 활성화 업데이트
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    
    startQuiz();
}

// 퀴즈 시작
function startQuiz() {
    currentQuestion = 0;
    score = 0;
    answersRecord = [];
    selectedAnswer = null;
    isAnswered = false;
    
    const questions = roundData[currentRound];
    if (!questions || questions.length === 0) {
        alert(`${currentRound}회 문제 데이터가 없습니다.`);
        return;
    }
    
    // 초기 메시지 숨기고 퀴즈 콘텐츠 표시
    const selectMessage = document.getElementById('select-round-message');
    const quizContent = document.getElementById('quiz-content');
    const finalResult = document.getElementById('final-result');
    const questionNav = document.getElementById('question-nav');
    const restartButton = document.querySelector('.restart-quiz-button');
    
    if (selectMessage) selectMessage.style.display = 'none';
    if (quizContent) quizContent.style.display = 'block';
    if (finalResult) finalResult.style.display = 'none';
    if (questionNav) questionNav.style.display = 'grid';
    if (restartButton) restartButton.style.display = 'inline-block';
    
    // 점수 초기화
    document.getElementById('score').textContent = '0';
    
    // 답안 기록 초기화
    for (let i = 0; i < questions.length; i++) {
        answersRecord.push({
            answered: false,
            correct: false,
            selectedAnswer: null
        });
    }
    
    displayQuestion();
    createQuestionNavigation();
}

// 문제 표시
function displayQuestion() {
    const questions = roundData[currentRound];
    const question = questions[currentQuestion];
    
    document.getElementById('current-round').textContent = `${currentRound}회`;
    document.getElementById('question-text').innerHTML = `${currentQuestion + 1}. ${question.question}`;
    
    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = '';
    
    const optionMarkers = ['①', '②', '③', '④'];
    question.options.forEach((option, index) => {
        const button = document.createElement('button');
        button.className = 'option-button';
        button.innerHTML = `${optionMarkers[index]} ${option}`;
        button.onclick = () => selectAnswer(index);
        optionsContainer.appendChild(button);
    });
    
    document.getElementById('explanation').style.display = 'none';
    document.getElementById('explanation-text').textContent = '';
    document.getElementById('result').style.display = 'none';
    document.getElementById('next-button').style.display = 'none';
    document.getElementById('check-button').style.display = 'inline-block';
    document.getElementById('check-button').disabled = true;
    
    selectedAnswer = null;
    isAnswered = false;
    
    // 이전에 답한 문제면 결과 표시
    if (answersRecord[currentQuestion].answered) {
        selectedAnswer = answersRecord[currentQuestion].selectedAnswer;
        isAnswered = true;
        
        const buttons = document.querySelectorAll('.option-button');
        const correct = question.correct;
        buttons.forEach((btn, index) => {
            if (index === correct) {
                btn.classList.add('correct');
            } else if (index === selectedAnswer) {
                btn.classList.add('wrong');
            }
            if (index === selectedAnswer) {
                btn.classList.add('selected');
            }
        });
        
        document.getElementById('explanation').style.display = 'block';
        document.getElementById('explanation-text').innerHTML = question.explanation;
        document.getElementById('check-button').style.display = 'none';
        document.getElementById('next-button').style.display = 'inline-block';
    }
    
    updateButtonStates();
}

// 답안 선택
function selectAnswer(index) {
    if (isAnswered) return;
    
    selectedAnswer = index;
    
    const buttons = document.querySelectorAll('.option-button');
    buttons.forEach((btn, i) => {
        btn.classList.remove('selected');
        if (i === index) {
            btn.classList.add('selected');
        }
    });
    
    document.getElementById('check-button').disabled = false;
    updateButtonStates();
}

// 답안 확인
function checkAnswer() {
    if (selectedAnswer === null || isAnswered) return;
    
    const questions = roundData[currentRound];
    const question = questions[currentQuestion];
    const correct = question.correct;
    
    isAnswered = true;
    
    answersRecord[currentQuestion].answered = true;
    answersRecord[currentQuestion].selectedAnswer = selectedAnswer;
    answersRecord[currentQuestion].correct = (selectedAnswer === correct);
    
    if (selectedAnswer === correct) {
        score += 2;
    }
    
    const buttons = document.querySelectorAll('.option-button');
    buttons.forEach((btn, index) => {
        btn.classList.remove('selected');
        if (index === correct) {
            btn.classList.add('correct');
        } else if (index === selectedAnswer) {
            btn.classList.add('wrong');
        }
    });
    
    document.getElementById('explanation').style.display = 'block';
    document.getElementById('explanation-text').innerHTML = question.explanation;
    document.getElementById('score').textContent = score;
    
    document.getElementById('check-button').style.display = 'none';
    document.getElementById('next-button').style.display = 'inline-block';
    
    updateQuestionNavigation();
    updateButtonStates();
}

// 다음 문제
function nextQuestion() {
    const questions = roundData[currentRound];
    if (currentQuestion < questions.length - 1) {
        currentQuestion++;
        displayQuestion();
        updateQuestionNavigation();
    }
}

// 이전 문제
function previousQuestion() {
    if (currentQuestion > 0) {
        currentQuestion--;
        displayQuestion();
        updateQuestionNavigation();
    }
}

// 문제 번호 네비게이션 생성
function createQuestionNavigation() {
    const questions = roundData[currentRound];
    const container = document.getElementById('question-nav');
    container.innerHTML = '';
    
    for (let i = 0; i < questions.length; i++) {
        const button = document.createElement('button');
        button.className = 'question-number-btn';
        button.textContent = i + 1;
        button.onclick = () => goToQuestion(i);
        
        if (i === currentQuestion) {
            button.classList.add('active');
        }
        
        container.appendChild(button);
    }
    
    updateQuestionNavigation();
}

// 문제 번호 네비게이션 업데이트
function updateQuestionNavigation() {
    const buttons = document.querySelectorAll('.question-number-btn');
    buttons.forEach((btn, index) => {
        btn.classList.remove('active', 'answered-correct', 'answered-wrong');
        
        if (index === currentQuestion) {
            btn.classList.add('active');
        }
        
        if (answersRecord[index].answered) {
            if (answersRecord[index].correct) {
                btn.classList.add('answered-correct');
            } else {
                btn.classList.add('answered-wrong');
            }
        }
    });
}

// 특정 문제로 이동
function goToQuestion(index) {
    currentQuestion = index;
    displayQuestion();
    updateQuestionNavigation();
}

// 퀴즈 재시작
function restartQuiz() {
    showModal(
        '🔄 퀴즈 다시 시작',
        '현재 진행 상황이 모두 초기화됩니다.\n처음부터 다시 시작하시겠습니까?',
        () => {
            startQuiz();
        }
    );
}

// 틀린 문제만 다시 풀기
function reviewWrongAnswers() {
    const wrongQuestions = answersRecord
        .map((record, index) => record.answered && !record.correct ? index : -1)
        .filter(index => index !== -1);
    
    if (wrongQuestions.length === 0) {
        showModal(
            '✅ 완벽합니다!',
            '틀린 문제가 없습니다!\n모든 문제를 정확하게 풀이하셨습니다.',
            null,
            true
        );
        return;
    }
    
    showModal(
        '📝 틀린 문제 복습',
        `틀린 문제 ${wrongQuestions.length}개를 다시 풀이하시겠습니까?`,
        () => {
            currentQuestion = wrongQuestions[0];
            
            wrongQuestions.forEach(index => {
                answersRecord[index].answered = false;
                answersRecord[index].correct = false;
                answersRecord[index].selectedAnswer = null;
            });
            
            displayQuestion();
            updateQuestionNavigation();
        }
    );
}

// 버튼 상태 업데이트
function updateButtonStates() {
    const checkBtn = document.getElementById('check-button');
    const nextBtn = document.getElementById('next-button');
    
    if (checkBtn) {
        checkBtn.disabled = (selectedAnswer === null || isAnswered);
    }
}

// 섹션 표시
function showSection(sectionId) {
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    if (sectionId === 'home') {
        document.getElementById('home-section').classList.add('active');
    }
    
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
}

// 페이지 로드 시 초기화
window.onload = function() {
    showSection('home');
    
    // roundData 객체가 로드되었는지 확인
    if (typeof roundData === 'undefined') {
        console.error('roundData가 로드되지 않았습니다. quiz_all_data.js 파일을 확인하세요.');
        alert('문제 데이터를 로드하는 중 오류가 발생했습니다.');
    } else {
        console.log('데이터 로드 완료:', Object.keys(roundData).length + '개 회차');
    }
};

// 모바일 메뉴 토글
function toggleMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const body = document.body;
    
    sidebar.classList.toggle('active');
    
    // 오버레이 생성/제거
    let overlay = document.querySelector('.mobile-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'mobile-overlay';
        overlay.onclick = toggleMobileMenu;
        body.appendChild(overlay);
    }
    
    overlay.classList.toggle('active');
}

// 정답 PDF 보기
function viewAnswer(event, round) {
    event.stopPropagation(); // 부모 버튼 클릭 방지
    
    const pdfModal = document.getElementById('pdf-modal');
    const pdfViewer = document.getElementById('pdf-viewer');
    const pdfTitle = document.getElementById('pdf-title');
    
    pdfTitle.textContent = `${round}회 정답`;
    pdfViewer.src = `anser/${round}A.pdf`;
    pdfModal.style.display = 'flex';
    
    // 모바일 환경에서 자동으로 가로에 맞게 축소
    setTimeout(() => {
        if (window.innerWidth <= 768) {
            currentZoom = 60; // 모바일에서 60%로 시작
        } else {
            currentZoom = 100; // 데스크톱에서 100%
        }
        updateZoom();
    }, 100);
}

// 정답 PDF 다운로드
function downloadAnswer(event, round) {
    event.stopPropagation(); // 부모 버튼 클릭 방지
    
    const link = document.createElement('a');
    link.href = `anser/${round}A.pdf`;
    link.download = `${round}회_정답.pdf`;
    link.click();
}

// PDF 모달 닫기
function closePdfModal() {
    const pdfModal = document.getElementById('pdf-modal');
    const pdfViewer = document.getElementById('pdf-viewer');
    
    pdfModal.style.display = 'none';
    pdfViewer.src = ''; // PDF 로드 중지
    resetZoom(); // 줌 레벨 초기화
}

// PDF 줌 기능
let currentZoom = 100;

function zoomIn() {
    if (currentZoom < 200) {
        currentZoom += 10;
        updateZoom();
    }
}

function zoomOut() {
    if (currentZoom > 50) {
        currentZoom -= 10;
        updateZoom();
    }
}

function resetZoom() {
    if (window.innerWidth <= 768) {
        currentZoom = 60; // 모바일에서 60%
    } else {
        currentZoom = 100; // 데스크톱에서 100%
    }
    updateZoom();
}

function updateZoom() {
    const pdfViewer = document.getElementById('pdf-viewer');
    const zoomLevel = document.getElementById('zoom-level');
    if (pdfViewer && zoomLevel) {
        pdfViewer.style.transform = `scale(${currentZoom / 100})`;
        pdfViewer.style.transformOrigin = 'top center';
        zoomLevel.textContent = `${currentZoom}%`;
    }
}
