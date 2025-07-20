import 'dotenv/config';
import { TavilySearch } from '@langchain/tavily';

// 定义 tools
const agentTools = [
    new TavilySearch({
        maxResults: 3 // 最多查询 3 个结果
    })
];
import { ChatDeepSeek } from '@langchain/deepseek';
import { ChatAnthropic } from '@langchain/anthropic';
// 定义 llm
// const agentModel = new ChatDeepSeek({ model: 'deepseek-chat', temperature: 0 })
const agentModel = new ChatAnthropic({
    model: 'claude-sonnet-4-20250514',
    temperature: 0.1,
    maxTokens: 2000
});
import { MemorySaver } from '@langchain/langgraph';
import { createReactAgent } from '@langchain/langgraph/prebuilt';

// Initialize memory to persist state between graph runs
const agentCheckpoint = new MemorySaver();

// Create agent
const agent = createReactAgent({
    llm: agentModel, // 使用之前创建的 llm
    tools: agentTools, // 使用之前创建的 tools
    checkpointSaver: agentCheckpoint // 记忆，保存状态数据
});

import { HumanMessage } from '@langchain/core/messages';
import readline from 'readline';

// // test1
// const agentFinalState = await agent.invoke(
//     { messages: [new HumanMessage('中国北京天气怎么样')] },
//     { configurable: { thread_id: '1' } }
// );
// console.log(
//     agentFinalState.messages[agentFinalState.messages.length - 1].content
// );

// // test2
// const agentNextState = await agent.invoke(
//     { messages: [new HumanMessage('天津呢')] },
//     { configurable: { thread_id: '1' } }
// );
// console.log(
//     agentNextState.messages[agentNextState.messages.length - 1].content
// );

// test3: 使用 stream 流式输出
// streaming
// const stream = await agent.stream(
//     { messages: [new HumanMessage('中国西安天气怎么样')] },
//     { configurable: { thread_id: '1' }, streamMode: 'updates' }
// );
// let lastPrinted = '';
// for await (const step of stream) {
//     const messages = step.agent?.messages || step.messages || [];
//     if (messages.length === 0) continue;
//     const lastMsg = messages[messages.length - 1];
//     if (!lastMsg || !lastMsg.content) continue;
//
//     if (typeof lastMsg.content === 'string') {
//         if (lastMsg.content !== lastPrinted) {
//             console.log(lastMsg.content);
//             lastPrinted = lastMsg.content;
//         }
//     } else if (Array.isArray(lastMsg.content)) {
//         for (const part of lastMsg.content) {
//             if (part.type === 'text' && part.text !== lastPrinted) {
//                 console.log(part.text);
//                 lastPrinted = part.text;
//             }
//         }
//     }
// }

async function main() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    function ask(question) {
        return new Promise(resolve => rl.question(question, resolve));
    }

    const location = await ask('你想知道哪里的天气？\n');
    if (!location) {
        console.log('未输入地点，程序结束。');
        rl.close();
        return;
    }
    const streamChoice = await ask('是否需要流式输出？（输入“是”或直接回车为流式，否则为非流式）\n');
    rl.close();

    const prompt = `${location}天气怎么样`;
    const threadId = '1';
    if (!streamChoice || streamChoice.trim() === '是') {
        // 流式输出
        const stream = await agent.stream(
            { messages: [new HumanMessage(prompt)] },
            { configurable: { thread_id: threadId }, streamMode: 'updates' }
        );
        let lastPrinted = '';
        for await (const step of stream) {
            const messages = step.agent?.messages || step.messages || [];
            if (messages.length === 0) continue;
            const lastMsg = messages[messages.length - 1];
            if (!lastMsg || !lastMsg.content) continue;

            if (typeof lastMsg.content === 'string') {
                if (lastMsg.content !== lastPrinted) {
                    process.stdout.write(lastMsg.content + '\n');
                    lastPrinted = lastMsg.content;
                }
            } else if (Array.isArray(lastMsg.content)) {
                for (const part of lastMsg.content) {
                    if (part.type === 'text' && part.text !== lastPrinted) {
                        process.stdout.write(part.text + '\n');
                        lastPrinted = part.text;
                    }
                }
            }
        }
    } else {
        // 非流式输出
        const result = await agent.invoke(
            { messages: [new HumanMessage(prompt)] },
            { configurable: { thread_id: threadId } }
        );
        console.log(
            result.messages[result.messages.length - 1].content
        );
    }
}

main();
