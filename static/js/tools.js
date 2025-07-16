// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded, initializing tools...');

    // 为所有工具卡片添加点击事件
    const toolCards = document.querySelectorAll('.tool-card');
    console.log('Found tool cards:', toolCards.length);

    toolCards.forEach(card => {
        card.addEventListener('click', function () {
            const toolType = this.getAttribute('data-tool');
            console.log('Tool card clicked:', toolType);
            openToolModal(toolType);
        });
    });
});

// 打开工具模态框
function openToolModal(toolType) {
    console.log('Opening modal for:', toolType);

    const modalContainer = document.getElementById('tool-modals-container');
    if (!modalContainer) {
        console.error('Modal container not found!');
        return;
    }

    // 清除之前的模态框
    modalContainer.innerHTML = '';

    // 根据工具类型创建相应的模态框
    const modal = createToolModal(toolType);
    modalContainer.appendChild(modal);

    // 显示模态框
    modal.style.display = 'block';
    console.log('Modal displayed');

    // 添加关闭事件
    const closeBtn = modal.querySelector('.close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    // 点击模态框外部关闭
    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// 创建工具模态框
function createToolModal(toolType) {
    const modal = document.createElement('div');
    modal.className = 'tool-modal';
    modal.id = `modal-${toolType}`;

    let modalContent = '';

    switch (toolType) {
        case 'base64':
            modalContent = createBase64Modal();
            break;
        case 'hex':
            modalContent = createHexModal();
            break;
        case 'caesar':
            modalContent = createCaesarModal();
            break;
        case 'hash':
            modalContent = createHashModal();
            break;
        case 'url':
            modalContent = createUrlModal();
            break;
        case 'binary':
            modalContent = createBinaryModal();
            break;
        case 'json':
            modalContent = createJsonModal();
            break;
        case 'regex':
            modalContent = createRegexModal();
            break;
        default:
            modalContent = '<div class="modal-content"><p>工具开发中...</p></div>';
    }

    modal.innerHTML = modalContent;
    return modal;
}

// Base64 工具模态框
function createBase64Modal() {
    return `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Base64 编码/解码</h2>
                <span class="close">&times;</span>
            </div>
            <div class="modal-body">
                <div class="tool-section">
                    <label for="base64-input">输入文本:</label>
                    <textarea id="base64-input" placeholder="请输入要编码/解码的文本"></textarea>
                </div>
                <div class="tool-buttons">
                    <button onclick="encodeBase64()">编码</button>
                    <button onclick="decodeBase64()">解码</button>
                    <button onclick="clearBase64()">清空</button>
                </div>
                <div class="tool-section">
                    <label for="base64-output">输出结果:</label>
                    <textarea id="base64-output" readonly></textarea>
                </div>
            </div>
        </div>
    `;
}

// Hex 工具模态框
function createHexModal() {
    return `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Hex 十六进制转换</h2>
                <span class="close">&times;</span>
            </div>
            <div class="modal-body">
                <div class="tool-section">
                    <label for="hex-input">输入:</label>
                    <textarea id="hex-input" placeholder="请输入文本或十六进制"></textarea>
                </div>
                <div class="tool-buttons">
                    <button onclick="textToHex()">文本转Hex</button>
                    <button onclick="hexToText()">Hex转文本</button>
                    <button onclick="clearHex()">清空</button>
                </div>
                <div class="tool-section">
                    <label for="hex-output">输出结果:</label>
                    <textarea id="hex-output" readonly></textarea>
                </div>
            </div>
        </div>
    `;
}

// 其他工具模态框（简化版本）
function createCaesarModal() {
    return `
        <div class="modal-content">
            <div class="modal-header">
                <h2>凯撒密码</h2>
                <span class="close">&times;</span>
            </div>
            <div class="modal-body">
                <div class="tool-section">
                    <label for="caesar-input">输入文本:</label>
                    <textarea id="caesar-input" placeholder="请输入要加密/解密的文本"></textarea>
                </div>
                <div class="tool-section">
                    <label for="caesar-shift">偏移量:</label>
                    <input type="number" id="caesar-shift" value="3" min="1" max="25">
                </div>
                <div class="tool-buttons">
                    <button onclick="encryptCaesar()">加密</button>
                    <button onclick="decryptCaesar()">解密</button>
                    <button onclick="bruteForceCaesar()">暴力破解</button>
                </div>
                <div class="tool-section">
                    <label for="caesar-output">输出结果:</label>
                    <textarea id="caesar-output" readonly></textarea>
                </div>
            </div>
        </div>
    `;
}

// 简化的其他工具模态框
function createHashModal() {
    return `<div class="modal-content"><div class="modal-header"><h2>Hash 计算</h2><span class="close">&times;</span></div><div class="modal-body"><p>Hash工具开发中...</p></div></div>`;
}

function createUrlModal() {
    return `<div class="modal-content"><div class="modal-header"><h2>URL 编码/解码</h2><span class="close">&times;</span></div><div class="modal-body"><p>URL工具开发中...</p></div></div>`;
}

function createBinaryModal() {
    return `<div class="modal-content"><div class="modal-header"><h2>二进制转换</h2><span class="close">&times;</span></div><div class="modal-body"><p>二进制工具开发中...</p></div></div>`;
}

function createJsonModal() {
    return `<div class="modal-content"><div class="modal-header"><h2>JSON 格式化</h2><span class="close">&times;</span></div><div class="modal-body"><p>JSON工具开发中...</p></div></div>`;
}

function createRegexModal() {
    return `<div class="modal-content"><div class="modal-header"><h2>正则表达式测试</h2><span class="close">&times;</span></div><div class="modal-body"><p>正则工具开发中...</p></div></div>`;
}

// 工具函数
function encodeBase64() {
    const input = document.getElementById('base64-input').value;
    const output = document.getElementById('base64-output');
    try {
        output.value = btoa(unescape(encodeURIComponent(input)));
    } catch (e) {
        output.value = '编码失败: ' + e.message;
    }
}

function decodeBase64() {
    const input = document.getElementById('base64-input').value;
    const output = document.getElementById('base64-output');
    try {
        output.value = decodeURIComponent(escape(atob(input)));
    } catch (e) {
        output.value = '解码失败: ' + e.message;
    }
}

function clearBase64() {
    document.getElementById('base64-input').value = '';
    document.getElementById('base64-output').value = '';
}

function textToHex() {
    const input = document.getElementById('hex-input').value;
    const output = document.getElementById('hex-output');
    let hex = '';
    for (let i = 0; i < input.length; i++) {
        hex += input.charCodeAt(i).toString(16).padStart(2, '0');
    }
    output.value = hex;
}

function hexToText() {
    const input = document.getElementById('hex-input').value;
    const output = document.getElementById('hex-output');
    try {
        let text = '';
        for (let i = 0; i < input.length; i += 2) {
            text += String.fromCharCode(parseInt(input.substr(i, 2), 16));
        }
        output.value = text;
    } catch (e) {
        output.value = '转换失败: ' + e.message;
    }
}

function clearHex() {
    document.getElementById('hex-input').value = '';
    document.getElementById('hex-output').value = '';
}

function encryptCaesar() {
    const input = document.getElementById('caesar-input').value;
    const shift = parseInt(document.getElementById('caesar-shift').value);
    const output = document.getElementById('caesar-output');

    let result = '';
    for (let i = 0; i < input.length; i++) {
        let char = input[i];
        if (char.match(/[a-z]/i)) {
            let code = input.charCodeAt(i);
            if (code >= 65 && code <= 90) {
                char = String.fromCharCode(((code - 65 + shift) % 26) + 65);
            } else if (code >= 97 && code <= 122) {
                char = String.fromCharCode(((code - 97 + shift) % 26) + 97);
            }
        }
        result += char;
    }
    output.value = result;
}

function decryptCaesar() {
    const input = document.getElementById('caesar-input').value;
    const shift = parseInt(document.getElementById('caesar-shift').value);
    document.getElementById('caesar-shift').value = 26 - shift;
    encryptCaesar();
    document.getElementById('caesar-shift').value = shift;
}

function bruteForceCaesar() {
    const input = document.getElementById('caesar-input').value;
    const output = document.getElementById('caesar-output');
    let result = '';

    for (let shift = 1; shift <= 25; shift++) {
        let decoded = '';
        for (let i = 0; i < input.length; i++) {
            let char = input[i];
            if (char.match(/[a-z]/i)) {
                let code = input.charCodeAt(i);
                if (code >= 65 && code <= 90) {
                    char = String.fromCharCode(((code - 65 - shift + 26) % 26) + 65);
                } else if (code >= 97 && code <= 122) {
                    char = String.fromCharCode(((code - 97 - shift + 26) % 26) + 97);
                }
            }
            decoded += char;
        }
        result += `偏移 ${shift}: ${decoded}\n`;
    }
    output.value = result;
}