

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initAnimations();
    initToasts();
    injectSkillRecommendations();
});


function extractUserPerformance() {
    const statCards = document.querySelectorAll('.stat-card');
    let avgScore = null;
    
    statCards.forEach(card => {
        const label = card.querySelector('.stat-label')?.innerText || "";
        if (label.includes("Average Score")) {
            const valueStr = card.querySelector('.stat-value')?.innerText || "0";
            avgScore = parseInt(valueStr.replace('%', ''));
        }
    });
    
    return avgScore;
}

function injectSkillRecommendations() {
    const mainContent = document.querySelector('.dashboard-main') || document.querySelector('.main-column');
    if (!mainContent) return;

    const pageHeading = document.querySelector('h1')?.innerText || document.querySelector('.page-title')?.innerText || "";
    const subjectName = document.querySelector('.current-learning-card h2')?.innerText || "";
    const context = (pageHeading + " " + subjectName).toLowerCase();

    const userScore = extractUserPerformance();
    const isDashboard = window.location.pathname.includes('/dashboard');

    const skillMap = [
        {
            keywords: ['python', 'coding', 'programming', 'script'],
            skill: 'Python Development',
            strong: { msg: 'You have mastered Python basics. You are now ready to transition into AI & Data Science.', level: 'Strong', badge: 'badge-strong', primary: 'Explore AI/DS', pLink: '/subjects?category=Data Science', secondary: 'Advanced OOPS', sLink: '/subjects' },
            moderate: { msg: 'Your Python skills are improving. Focus on Advanced Projects to build more confidence.', level: 'Moderate', badge: 'badge-moderate', primary: 'Build Projects', pLink: '/generator', secondary: 'Advanced Method', sLink: '/subjects' },
            weak: { msg: 'Let\'s strengthen your foundations. Revision of core Python logic will help you progress faster.', level: 'Weak', badge: 'badge-weak', primary: 'Review Basics', pLink: '/learning_path', secondary: 'Ask AI Mentor', sLink: '/chat' }
        },
        {
            keywords: ['aptitude', 'logic', 'reasoning', 'math'],
            skill: 'Quantitative Aptitude',
            strong: { msg: 'Exemplary logical reasoning. This is your core strength for GATE and Government Exams.', level: 'Strong', badge: 'badge-strong', primary: 'Explore GATE', pLink: '/subjects?category=GATE', secondary: 'Mock Tests', sLink: '/subjects' },
            moderate: { msg: 'You are on the right track. Practice more sets to decrease your problem-solving time.', level: 'Moderate', badge: 'badge-moderate', primary: 'Practice More', pLink: '/subjects', secondary: 'Govt Prep', sLink: '/subjects?category=Government Exams' },
            weak: { msg: 'Solving basic math modules will build your speed. Let\'s revisit the fundamentals together.', level: 'Weak', badge: 'badge-weak', primary: 'Revisit Fundamentals', pLink: '/learning_path', secondary: 'Consult Mentor', sLink: '/chat' }
        }
    ];

    const match = skillMap.find(s => s.keywords.some(k => context.includes(k)));
    if (!match) return;

    let guidance = null;
    if (userScore === null) {
        guidance = match.moderate;
        guidance.msg = `You are currently mastering ${match.skill}. AI Analysis suggests focus on consistency.`;
    } else if (userScore > 75) {
        guidance = match.strong;
    } else if (userScore >= 40) {
        guidance = match.moderate;
    } else {
        guidance = match.weak;
    }

    const scoreVal = userScore || 50; 
    const progressColor = userScore > 75 ? '#10b981' : (userScore >= 40 ? '#f59e0b' : '#ef4444');

    const card = document.createElement('div');
    card.className = 'skill-rec-card glass-card';
    card.innerHTML = `
        <div class="ai-insight-header">
            <div class="ai-label">
                <span class="material-icons" style="font-size:16px">auto_awesome</span>
                Smart AI Insight
            </div>
            <div class="performance-badge ${guidance.badge}">${guidance.level} Proficiency</div>
        </div>
        
        <div class="skill-rec-body">
            <h3 class="skill-rec-title">Based on your performance in ${match.skill}</h3>
            <p class="skill-rec-desc">${guidance.msg}</p>
        </div>

        <div class="mini-progress-section">
            <div class="mini-progress-label">
                <span>Skill Mastery</span>
                <span>${scoreVal}%</span>
            </div>
            <div class="mini-progress-bg">
                <div class="mini-progress-fill" style="width: 0%; background: ${progressColor}"></div>
            </div>
        </div>

        <div class="skill-rec-actions">
            <a href="${guidance.pLink}" class="btn-ai-action btn-ai-primary">
                <span class="material-icons">rocket_launch</span>
                ${guidance.primary}
            </a>
            <a href="${guidance.sLink}" class="btn-ai-action btn-ai-secondary">
                <span class="material-icons">explore</span>
                ${guidance.secondary}
            </a>
        </div>
    `;

    const targetParent = document.querySelector('.main-column') || document.querySelector('.dashboard-main');
    if (targetParent) {
        const anchor = targetParent.querySelector('header') || targetParent.firstChild;
        targetParent.insertBefore(card, anchor.nextSibling);

        setTimeout(() => {
            const fill = card.querySelector('.mini-progress-fill');
            if (fill) fill.style.width = scoreVal + '%';
        }, 300);
    }
}


function initSidebar() {
    const toggleBtn = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('active');
            if (overlay) overlay.classList.toggle('active');
        });
        
        if (overlay) {
            overlay.addEventListener('click', () => {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            });
        }
    }
}


function initAnimations() {
    const elements = document.querySelectorAll('.animate-fade-up');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    elements.forEach(el => observer.observe(el));
}


function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="material-icons">${type === 'success' ? 'check_circle' : 'info'}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function initToasts() {
    const flashMessages = document.querySelectorAll('.flash-data');
    flashMessages.forEach(msg => {
        const category = msg.dataset.category || 'info';
        const message = msg.dataset.message;
        
        if (category === 'error' || category === 'danger') {
            showAlert(message, 'error');
        } else if (category.startsWith('modal-')) {
            const type = category.replace('modal-', '');
            showAlert(message, type);
        } else {
            showToast(message, category);
        }
    });
}

function showAlert(message, type = 'info') {
    const modal = document.getElementById('alert-modal');
    const title = document.getElementById('alert-title');
    const msg = document.getElementById('alert-message');
    const iconCon = document.getElementById('alert-icon-container');
    const closeBtn = document.getElementById('close-alert');
    const okBtn = document.getElementById('btn-alert-ok');

    if (!modal) return;

    title.innerText = type.charAt(0).toUpperCase() + type.slice(1);
    msg.innerText = message;
    
    let icon = 'info';
    let color = 'var(--primary)';
    if (type === 'error' || type === 'danger') {
        icon = 'error_outline';
        color = '#ef4444';
        title.innerText = 'Login Unsuccessful';
    } else if (type === 'success') {
        icon = 'check_circle_outline';
        color = '#10b981';
        title.innerText = 'Account Verified';
    } else if (type === 'info') {
        icon = 'mark_email_read';
        color = '#3b82f6';
        title.innerText = 'OTP Sent';
    }

    iconCon.innerHTML = `<span class="material-icons" style="font-size: 64px; color: ${color}">${icon}</span>`;
    
    modal.style.display = 'block';

    const close = () => {
        modal.style.display = 'none';
    };

    closeBtn.onclick = close;
    okBtn.onclick = close;
    window.onclick = (event) => {
        if (event.target == modal) close();
    };
}
