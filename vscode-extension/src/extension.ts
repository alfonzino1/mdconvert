import * as vscode from 'vscode';

// ============================================================
// CONVERTER ENGINE (ported from Python/JS)
// ============================================================

interface ConversionResult {
    markdown: string;
    stats: {
        originalChars: number;
        markdownChars: number;
        tokensSaved: number;
        compression: string;
        elements: {
            headers: number;
            lists: number;
            code: number;
            tasks: number;
            quotes: number;
        };
    };
}

class MarkdownConverter {
    convert(text: string): ConversionResult {
        if (!text.trim()) {
            return {
                markdown: '',
                stats: {
                    originalChars: 0, markdownChars: 0, tokensSaved: 0,
                    compression: '0', elements: { headers: 0, lists: 0, code: 0, tasks: 0, quotes: 0 }
                }
            };
        }

        const lines = text.split('\n');
        const result: string[] = [];
        const elements = { headers: 0, lists: 0, code: 0, tasks: 0, quotes: 0 };

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const stripped = line.trim();

            if (!stripped) { result.push(''); continue; }

            // H1: first non-empty line
            if (i === 0 && stripped.length < 100 && !stripped.startsWith('#')) {
                result.push(`# ${stripped}`);
                elements.headers++;
                continue;
            }

            // H2: ends with colon
            if (stripped.endsWith(':') && stripped.length < 80 &&
                !stripped.startsWith('#') && !stripped.startsWith('-')) {
                result.push(`## ${stripped}`);
                elements.headers++;
                continue;
            }

            // H3: ALL CAPS
            if (stripped === stripped.toUpperCase() && stripped.length < 60 &&
                !stripped.startsWith('#') && /[A-Z]/.test(stripped) && !/^\d+$/.test(stripped)) {
                result.push(`### ${stripped}`);
                elements.headers++;
                continue;
            }

            // Numbered list
            const numMatch = stripped.match(/^(\d+)[.)]\s*(.+)/);
            if (numMatch) {
                result.push(`${numMatch[1]}. ${numMatch[2].trim()}`);
                elements.lists++;
                continue;
            }

            // Task list
            const taskMatch = stripped.match(/^\[([ xX])\]\s*(.+)/);
            if (taskMatch) {
                const checked = taskMatch[1].toLowerCase() === 'x' ? 'x' : ' ';
                result.push(`- [${checked}] ${taskMatch[2].trim()}`);
                elements.tasks++;
                continue;
            }

            // Bullet list
            if (/^[\-*+]\s/.test(stripped)) {
                result.push(`- ${stripped.slice(1).trim()}`);
                elements.lists++;
                continue;
            }

            // Blockquote
            if (stripped.startsWith('>')) {
                result.push(stripped);
                elements.quotes++;
                continue;
            }

            // Horizontal rule
            if (/^[\-*_]{3,}$/.test(stripped)) {
                result.push('---');
                continue;
            }

            // Code fence
            if (stripped.startsWith('```')) {
                result.push(stripped);
                elements.code++;
                continue;
            }

            result.push(line);
        }

        const markdown = result.join('\n').replace(/\n{3,}/g, '\n\n').trim();
        const originalTokens = Math.floor(text.split(/\s+/).length * 1.3);
        const markdownTokens = Math.floor(markdown.split(/\s+/).length * 1.3);
        const tokensSaved = Math.max(0, originalTokens - markdownTokens);
        const compression = text.length
            ? ((1 - markdown.length / text.length) * 100).toFixed(1)
            : '0';

        return {
            markdown,
            stats: {
                originalChars: text.length,
                markdownChars: markdown.length,
                tokensSaved,
                compression,
                elements
            }
        };
    }
}

// ============================================================
// EXTENSION
// ============================================================

const converter = new MarkdownConverter();

export function activate(context: vscode.ExtensionContext) {
    console.log('Markdown Converter activated');

    // Status bar item
    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.text = '$(markdown) MD Convert';
    statusBarItem.tooltip = 'Convert to Markdown';
    statusBarItem.command = 'mdconvert.convertSelection';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Command: Convert selection
    const convertSelectionCmd = vscode.commands.registerCommand(
        'mdconvert.convertSelection',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            const selection = editor.selection;
            const text = editor.document.getText(selection);

            if (!text) {
                vscode.window.showWarningMessage('No text selected');
                return;
            }

            const config = vscode.workspace.getConfiguration('mdconvert');
            const result = converter.convert(text);

            // Show quick pick with actions
            const action = await vscode.window.showQuickPick(
                [
                    {
                        label: '$(check) Apply',
                        description: 'Replace selection with Markdown',
                        action: 'apply'
                    },
                    {
                        label: '$(files) Open as New File',
                        description: 'Open result in new editor tab',
                        action: 'newFile'
                    },
                    {
                        label: '$(copy) Copy to Clipboard',
                        description: 'Copy Markdown to clipboard',
                        action: 'copy'
                    },
                    {
                        label: '$(preview) Preview',
                        description: 'Open Markdown preview',
                        action: 'preview'
                    }
                ],
                {
                    placeHolder: `Converted! ${result.stats.tokensSaved} tokens saved (${result.stats.compression}% smaller)`
                }
            );

            if (!action) return;

            switch (action.action) {
                case 'apply':
                    await editor.edit(editBuilder => {
                        editBuilder.replace(selection, result.markdown);
                    });
                    if (config.get('showStats')) {
                        showStatsNotification(result);
                    }
                    break;

                case 'newFile':
                    const doc = await vscode.workspace.openTextDocument({
                        content: result.markdown,
                        language: 'markdown'
                    });
                    await vscode.window.showTextDocument(doc);
                    break;

                case 'copy':
                    await vscode.env.clipboard.writeText(result.markdown);
                    vscode.window.showInformationMessage(
                        `$(copy) Copied! ${result.stats.tokensSaved} tokens saved`
                    );
                    break;

                case 'preview':
                    const previewDoc = await vscode.workspace.openTextDocument({
                        content: result.markdown,
                        language: 'markdown'
                    });
                    await vscode.window.showTextDocument(previewDoc);
                    await vscode.commands.executeCommand('markdown.showPreview');
                    break;
            }
        }
    );

    // Command: Convert whole document
    const convertCmd = vscode.commands.registerCommand(
        'mdconvert.convert',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            const text = editor.document.getText();
            if (!text.trim()) {
                vscode.window.showWarningMessage('Empty document');
                return;
            }

            const result = converter.convert(text);

            const doc = await vscode.workspace.openTextDocument({
                content: result.markdown,
                language: 'markdown'
            });
            await vscode.window.showTextDocument(doc);

            showStatsNotification(result);
        }
    );

    // Command: Copy as Markdown
    const copyAsMarkdownCmd = vscode.commands.registerCommand(
        'mdconvert.copyAsMarkdown',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) return;

            const text = editor.selection.isEmpty
                ? editor.document.getText()
                : editor.document.getText(editor.selection);

            if (!text) {
                vscode.window.showWarningMessage('No text to convert');
                return;
            }

            const result = converter.convert(text);
            await vscode.env.clipboard.writeText(result.markdown);

            vscode.window.showInformationMessage(
                `$(copy) Markdown copied! ~${result.stats.tokensSaved} tokens saved`
            );
        }
    );

    context.subscriptions.push(convertSelectionCmd, convertCmd, copyAsMarkdownCmd);
}

function showStatsNotification(result: ConversionResult) {
    const s = result.stats;
    vscode.window.showInformationMessage(
        `Converted: ${s.originalChars} → ${s.markdownChars} chars | ` +
        `~${s.tokensSaved} tokens saved (${s.compression}%) | ` +
        `${s.elements.headers}H ${s.elements.lists}L ${s.elements.tasks}T ${s.elements.quotes}Q`,
        { modal: false }
    );
}

export function deactivate() {}