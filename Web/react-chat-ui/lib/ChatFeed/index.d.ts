import * as React from 'react';
import Message from '../Message';
interface ChatFeedInterface {
    props: {
        bubblesCentered?: boolean;
        bubbleStyles?: object;
        hasInputField?: boolean;
        isTyping?: boolean;
        maxHeight?: number;
        messages: any;
        showSenderName?: boolean;
        chatBubble?: React.Component;
    };
}
export default class ChatFeed extends React.Component {
    props: any;
    chat: {
        scrollHeight: number;
        clientHeight: number;
        scrollTop: number;
    };
    constructor(props: ChatFeedInterface);
    componentDidMount(): void;
    componentDidUpdate(): void;
    scrollToBottom(): void;
    renderMessages(messages: [Message]): any[];
    render(): any;
}
export {};
