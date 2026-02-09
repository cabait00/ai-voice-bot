import './VoiceButton.css';

function VoiceButton({ isListening, isSpeaking, onStart, onStop, onStopSpeaking, disabled }) {
  const handleClick = () => {
    if (isSpeaking) {
      onStopSpeaking();
    } else if (isListening) {
      onStop();
    } else {
      onStart();
    }
  };

  const renderLabel = () => {
    if (isSpeaking) return 'Ausgabe stoppen';
    if (isListening) return 'Aufnahme stoppen';
    return 'Sprechen';
  };

  return (
    <div className="voice-button-container">
      <button
        className={`voice-button ${isListening ? 'listening' : ''} ${isSpeaking ? 'speaking' : ''}`}
        onClick={handleClick}
        disabled={disabled}
        type="button"
        aria-label={renderLabel()}
      >
        <div className="voice-button-inner">
          <div className="voice-dot" />
          <div className="voice-label">{renderLabel()}</div>
        </div>
      </button>
    </div>
  );
}

export default VoiceButton;
