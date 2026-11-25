/**
 * US VESTA - ADVANCED CUSTOM RICH TEXT EDITOR
 * Full-featured, responsive, watermark-free modern rich text editor.
 * Drops in cleanly to replace FroalaEditor everywhere in the CRM.
 */

(function () {
    class CustomRichEditor {
        constructor(target, options = {}) {
            this.target = typeof target === 'string' ? document.querySelector(target) : target;
            if (!this.target) return;

            // If already initialized, return existing instance
            if (this.target._customEditorInstance) {
                return this.target._customEditorInstance;
            }

            this.options = Object.assign({
                heightMin: options.heightMin || 200,
                heightMax: options.heightMax || 500,
                placeholder: options.placeholder || 'Start typing your content here...',
                showWordCount: true,
            }, options);

            this.isCodeView = false;
            this.isFullscreen = false;
            this.savedSelection = null;

            this.init();
            this.target._customEditorInstance = this;
        }

        init() {
            // Hide the original textarea
            this.target.style.display = 'none';

            // Create Container
            this.container = document.createElement('div');
            this.container.className = 'custom-editor-container';

            // Create Toolbar
            this.toolbar = document.createElement('div');
            this.toolbar.className = 'custom-editor-toolbar';
            this.buildToolbar();

            // Create Editable Area
            this.contentArea = document.createElement('div');
            this.contentArea.className = 'custom-editor-content';
            this.contentArea.contentEditable = true;
            this.contentArea.setAttribute('data-placeholder', this.options.placeholder);
            this.contentArea.style.minHeight = `${this.options.heightMin}px`;
            this.contentArea.style.maxHeight = `${this.options.heightMax}px`;

            // Initial Content
            this.contentArea.innerHTML = this.target.value || '';

            // Create Raw HTML Area
            this.rawHtmlArea = document.createElement('textarea');
            this.rawHtmlArea.className = 'custom-editor-raw-html';
            this.rawHtmlArea.style.minHeight = `${this.options.heightMin}px`;
            this.rawHtmlArea.style.maxHeight = `${this.options.heightMax}px`;

            // Create Status Bar
            this.statusBar = document.createElement('div');
            this.statusBar.className = 'custom-editor-statusbar';
            this.statusBar.innerHTML = `
                <div>
                    <span class="badge-mode" id="editorModeBadge">Visual</span>
                </div>
                <div>
                    <span id="editorStats">0 words | 0 chars</span>
                </div>
            `;

            // Append all elements
            this.container.appendChild(this.toolbar);
            this.container.appendChild(this.contentArea);
            this.container.appendChild(this.rawHtmlArea);
            this.container.appendChild(this.statusBar);

            // Insert after textarea
            this.target.parentNode.insertBefore(this.container, this.target.nextSibling);

            // Event Listeners
            this.bindEvents();
            this.updateStats();
        }

        buildToolbar() {
            this.toolbar.innerHTML = `
                <!-- History -->
                <div class="custom-editor-btn-group">
                    <button type="button" class="custom-editor-btn" data-command="undo" title="Undo (Ctrl+Z)"><i class="fas fa-undo"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="redo" title="Redo (Ctrl+Y)"><i class="fas fa-redo"></i></button>
                </div>

                <!-- Paragraph / Heading -->
                <select class="custom-editor-select" data-command="formatBlock" title="Heading Format">
                    <option value="<p>">Normal</option>
                    <option value="<h1>">Heading 1</option>
                    <option value="<h2>">Heading 2</option>
                    <option value="<h3>">Heading 3</option>
                    <option value="<h4>">Heading 4</option>
                    <option value="<blockquote>">Quote</option>
                    <option value="<pre>">Code Block</option>
                </select>

                <!-- Font Family -->
                <select class="custom-editor-select" data-command="fontName" title="Font Family">
                    <option value="'Outfit', sans-serif">Outfit</option>
                    <option value="'Inter', sans-serif">Inter</option>
                    <option value="Arial, sans-serif">Arial</option>
                    <option value="'Playfair Display', serif">Playfair</option>
                    <option value="Georgia, serif">Georgia</option>
                    <option value="Courier New, monospace">Monospace</option>
                </select>

                <!-- Font Size -->
                <select class="custom-editor-select" data-command="fontSize" title="Font Size">
                    <option value="3">Normal (14px)</option>
                    <option value="1">Small (10px)</option>
                    <option value="2">Medium (12px)</option>
                    <option value="4">Large (16px)</option>
                    <option value="5">X-Large (18px)</option>
                    <option value="6">2X-Large (24px)</option>
                    <option value="7">3X-Large (32px)</option>
                </select>

                <!-- Basic Formatting -->
                <div class="custom-editor-btn-group">
                    <button type="button" class="custom-editor-btn" data-command="bold" title="Bold (Ctrl+B)"><i class="fas fa-bold"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="italic" title="Italic (Ctrl+I)"><i class="fas fa-italic"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="underline" title="Underline (Ctrl+U)"><i class="fas fa-underline"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="strikeThrough" title="Strikethrough"><i class="fas fa-strikethrough"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="subscript" title="Subscript"><i class="fas fa-subscript"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="superscript" title="Superscript"><i class="fas fa-superscript"></i></button>
                </div>

                <!-- Colors -->
                <div class="custom-editor-btn-group">
                    <label class="custom-editor-btn custom-editor-color-wrapper" title="Text Color">
                        <i class="fas fa-font" style="border-bottom: 3px solid #000; padding-bottom: 1px;"></i>
                        <input type="color" data-command="foreColor" value="#000000">
                    </label>
                    <label class="custom-editor-btn custom-editor-color-wrapper" title="Highlight / Background Color">
                        <i class="fas fa-highlighter" style="color: #c5a059;"></i>
                        <input type="color" data-command="hiliteColor" value="#ffff00">
                    </label>
                </div>

                <!-- Alignment -->
                <div class="custom-editor-btn-group">
                    <button type="button" class="custom-editor-btn" data-command="justifyLeft" title="Align Left"><i class="fas fa-align-left"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="justifyCenter" title="Align Center"><i class="fas fa-align-center"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="justifyRight" title="Align Right"><i class="fas fa-align-right"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="justifyFull" title="Justify"><i class="fas fa-align-justify"></i></button>
                </div>

                <!-- Lists & Indent -->
                <div class="custom-editor-btn-group">
                    <button type="button" class="custom-editor-btn" data-command="insertUnorderedList" title="Bullet List"><i class="fas fa-list-ul"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="insertOrderedList" title="Numbered List"><i class="fas fa-list-ol"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="outdent" title="Outdent"><i class="fas fa-outdent"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="indent" title="Indent"><i class="fas fa-indent"></i></button>
                </div>

                <!-- Insert Media & Elements -->
                <div class="custom-editor-btn-group">
                    <button type="button" class="custom-editor-btn" data-action="link" title="Insert Link"><i class="fas fa-link"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="unlink" title="Remove Link"><i class="fas fa-unlink"></i></button>
                    <button type="button" class="custom-editor-btn" data-action="image" title="Insert Image"><i class="fas fa-image"></i></button>
                    <button type="button" class="custom-editor-btn" data-action="table" title="Insert Table"><i class="fas fa-table"></i></button>
                    <button type="button" class="custom-editor-btn" data-command="insertHorizontalRule" title="Horizontal Line"><i class="fas fa-minus"></i></button>
                </div>

                <!-- Tools -->
                <div class="custom-editor-btn-group">
                    <button type="button" class="custom-editor-btn" data-command="removeFormat" title="Clear Formatting"><i class="fas fa-remove-format"></i></button>
                    <button type="button" class="custom-editor-btn" data-action="codeView" title="HTML Source Code View"><i class="fas fa-code"></i></button>
                    <button type="button" class="custom-editor-btn" data-action="fullscreen" title="Toggle Fullscreen"><i class="fas fa-expand"></i></button>
                </div>
            `;
        }

        bindEvents() {
            // Button Commands
            this.toolbar.querySelectorAll('.custom-editor-btn[data-command]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (this.isCodeView) return;
                    const command = btn.getAttribute('data-command');
                    this.executeCommand(command);
                });
            });

            // Select Dropdowns
            this.toolbar.querySelectorAll('select[data-command]').forEach(sel => {
                sel.addEventListener('change', (e) => {
                    if (this.isCodeView) return;
                    const command = sel.getAttribute('data-command');
                    const val = sel.value;
                    this.executeCommand(command, val);
                });
            });

            // Color Pickers
            this.toolbar.querySelectorAll('input[type="color"][data-command]').forEach(picker => {
                picker.addEventListener('input', (e) => {
                    if (this.isCodeView) return;
                    const command = picker.getAttribute('data-command');
                    this.executeCommand(command, picker.value);
                });
            });

            // Custom Actions (Link, Image, Table, CodeView, Fullscreen)
            this.toolbar.querySelectorAll('[data-action]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const action = btn.getAttribute('data-action');
                    if (action === 'codeView') this.toggleCodeView();
                    else if (action === 'fullscreen') this.toggleFullscreen();
                    else if (!this.isCodeView) {
                        if (action === 'link') this.promptLink();
                        else if (action === 'image') this.promptImage();
                        else if (action === 'table') this.promptTable();
                    }
                });
            });

            // Content Area Typing & Syncing
            this.contentArea.addEventListener('input', () => {
                this.sync();
                this.updateStats();
            });

            this.contentArea.addEventListener('blur', () => {
                this.sync();
            });

            // Raw HTML Area Syncing
            this.rawHtmlArea.addEventListener('input', () => {
                this.contentArea.innerHTML = this.rawHtmlArea.value;
                this.target.value = this.rawHtmlArea.value;
                this.updateStats();
            });

            // Sync on form submit automatically
            if (this.target.form) {
                this.target.form.addEventListener('submit', () => {
                    this.sync();
                });
            }
        }

        executeCommand(command, value = null) {
            this.contentArea.focus();
            document.execCommand(command, false, value);
            this.sync();
            this.updateStats();
        }

        saveSelection() {
            const sel = window.getSelection();
            if (sel.getRangeAt && sel.rangeCount) {
                this.savedSelection = sel.getRangeAt(0);
            }
        }

        restoreSelection() {
            if (this.savedSelection) {
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(this.savedSelection);
            }
        }

        promptLink() {
            this.saveSelection();
            const url = prompt("Enter hyperlink URL (e.g. https://example.com):", "https://");
            if (url && url !== "https://") {
                this.restoreSelection();
                this.executeCommand("createLink", url);
            }
        }

        promptImage() {
            this.saveSelection();
            const choice = confirm("Press OK to upload an image from your computer, or Cancel to enter an image URL.");
            if (choice) {
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.accept = 'image/*';
                fileInput.onchange = (e) => {
                    const file = e.target.files[0];
                    if (file) {
                        const reader = new FileReader();
                        reader.onload = (loadEvt) => {
                            this.restoreSelection();
                            this.executeCommand('insertImage', loadEvt.target.result);
                        };
                        reader.readAsDataURL(file);
                    }
                };
                fileInput.click();
            } else {
                const imgUrl = prompt("Enter image direct URL:");
                if (imgUrl) {
                    this.restoreSelection();
                    this.executeCommand('insertImage', imgUrl);
                }
            }
        }

        promptTable() {
            this.saveSelection();
            const rows = parseInt(prompt("Enter number of rows:", "3") || "3", 10);
            const cols = parseInt(prompt("Enter number of columns:", "3") || "3", 10);
            if (rows > 0 && cols > 0) {
                let html = '<table class="table table-bordered"><thead><tr>';
                for (let c = 1; c <= cols; c++) {
                    html += `<th>Header ${c}</th>`;
                }
                html += '</tr></thead><tbody>';
                for (let r = 1; r <= rows; r++) {
                    html += '<tr>';
                    for (let c = 1; c <= cols; c++) {
                        html += `<td>Row ${r} Col ${c}</td>`;
                    }
                    html += '</tr>';
                }
                html += '</tbody></table><p></p>';
                this.restoreSelection();
                this.insertHTML(html);
            }
        }

        insertHTML(html) {
            this.contentArea.focus();
            if (document.queryCommandSupported('insertHTML')) {
                document.execCommand('insertHTML', false, html);
            } else {
                const range = this.savedSelection || window.getSelection().getRangeAt(0);
                range.deleteContents();
                const div = document.createElement("div");
                div.innerHTML = html;
                const frag = document.createDocumentFragment();
                let node;
                while ((node = div.firstChild)) {
                    frag.appendChild(node);
                }
                range.insertNode(frag);
            }
            this.sync();
        }

        toggleCodeView() {
            this.isCodeView = !this.isCodeView;
            const codeBtn = this.toolbar.querySelector('[data-action="codeView"]');
            const modeBadge = this.statusBar.querySelector('#editorModeBadge');

            if (this.isCodeView) {
                this.rawHtmlArea.value = this.contentArea.innerHTML;
                this.contentArea.style.display = 'none';
                this.rawHtmlArea.style.display = 'block';
                this.rawHtmlArea.focus();
                if (codeBtn) codeBtn.classList.add('active');
                if (modeBadge) {
                    modeBadge.textContent = 'HTML Source';
                    modeBadge.style.background = '#e11d48';
                    modeBadge.style.color = '#fff';
                }
            } else {
                this.contentArea.innerHTML = this.rawHtmlArea.value;
                this.rawHtmlArea.style.display = 'none';
                this.contentArea.style.display = 'block';
                this.contentArea.focus();
                if (codeBtn) codeBtn.classList.remove('active');
                if (modeBadge) {
                    modeBadge.textContent = 'Visual';
                    modeBadge.style.background = '#e2e8f0';
                    modeBadge.style.color = '#334155';
                }
            }
            this.sync();
            this.updateStats();
        }

        toggleFullscreen() {
            this.isFullscreen = !this.isFullscreen;
            this.container.classList.toggle('fullscreen', this.isFullscreen);
            const fsBtn = this.toolbar.querySelector('[data-action="fullscreen"] i');
            if (fsBtn) {
                fsBtn.className = this.isFullscreen ? 'fas fa-compress' : 'fas fa-expand';
            }
        }

        sync() {
            const html = this.isCodeView ? this.rawHtmlArea.value : this.contentArea.innerHTML;
            this.target.value = html;
        }

        updateStats() {
            const text = (this.contentArea.innerText || '').trim();
            const words = text ? text.split(/\s+/).length : 0;
            const chars = text.length;
            const statsEl = this.statusBar.querySelector('#editorStats');
            if (statsEl) {
                statsEl.textContent = `${words} words | ${chars} chars`;
            }
        }

        getContent() {
            this.sync();
            return this.target.value;
        }

        getHTML() {
            return this.getContent();
        }

        setContent(html) {
            this.contentArea.innerHTML = html || '';
            this.rawHtmlArea.value = html || '';
            this.sync();
            this.updateStats();
        }

        html = {
            get: () => this.getContent(),
            set: (val) => this.setContent(val)
        };
    }

    // Expose Global Helper
    window.CustomRichEditor = CustomRichEditor;

    window.initCustomEditor = function (selector, options = {}) {
        const el = typeof selector === 'string' ? document.querySelector(selector) : selector;
        if (!el) return null;
        return new CustomRichEditor(el, options);
    };

    // Polyfill FroalaEditor constructor so ANY legacy Froala call works with ZERO code breakage!
    window.FroalaEditor = function (selector, options = {}) {
        return window.initCustomEditor(selector, options);
    };

    // Auto-init on DOMContentLoaded for common rich text areas
    document.addEventListener("DOMContentLoaded", function () {
        const defaultTargets = [
            "#productDescription",
            "#productHighlight",
            "#blog_content_editor",
            "#codinator_frola",
            "#coordinator_content_update"
        ];
        defaultTargets.forEach(sel => {
            const target = document.querySelector(sel);
            if (target && !target._customEditorInstance) {
                new CustomRichEditor(target);
            }
        });
    });
})();
