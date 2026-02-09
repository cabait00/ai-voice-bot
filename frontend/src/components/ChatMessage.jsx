import './ChatMessage.css';

function ChatMessage({ message }) {
  const { type, text, timestamp } = message;

  const formatTime = (date) => {
    return date.toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderAvatarText = () => {
    if (type === 'user') return 'DU';
    if (type === 'bot') return 'SCH';
    return 'I';
  };

  return (
    <div className={`chat-message ${type}`}>
      <div className="message-content">
        <div className={`avatar ${type}`}>{renderAvatarText()}</div>

        <div className="message-bubble">
          <p>{text}</p>
          <span className="timestamp">{formatTime(timestamp)}</span>
        </div>
      </div>
    </div>
  );
}

export default ChatMessage;
