import React, { useEffect, useState } from 'react';

export default function LongRunNotificationModal({
  defaultEmail,
  onConfirm,
  onCancel
}) {
  const [email, setEmail] = useState(defaultEmail || '');
  const [error, setError] = useState('');
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    if (defaultEmail) setEmail(defaultEmail);
  }, [defaultEmail]);

  const isValidEmail = (value) => /.+@.+\..+/.test(value);

  const handleSubmit = () => {
    if (!isValidEmail(email)) {
      setError('Please enter a valid email.');
      return;
    }
    setError('');
    setConfirming(true);
  };

  const handleConfirm = () => {
    if (typeof onConfirm === 'function') onConfirm(email);
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>This analysis might take a while</h3>
          <button className="close-button" onClick={onCancel}>×</button>
        </div>
        <div className="modal-body">
          {!confirming ? (
            <>
              <p>Based on your file size and selected methods, this run could be long. Would you like to get an email when it finishes?</p>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <input
                  type="email"
                  placeholder="Email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  style={{ flex: 1 }}
                />
                <button onClick={handleSubmit}>Notify me when finished</button>
              </div>
              <div style={{ marginTop: 8, fontSize: 12, color: '#6b7280' }}>
                Note: The notification email may land in your Spam/Junk folder. Please check there if it doesn't appear in your inbox.
              </div>
              {error && <div className="error-message" style={{ marginTop: 8 }}>{error}</div>}
              <div style={{ marginTop: 10 }}>
                <button onClick={onCancel}>No, thanks</button>
              </div>
            </>
          ) : (
            <>
              <p>We will notify: <b>{email}</b>. Confirm?</p>
              <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={handleConfirm}>Confirm</button>
                <button onClick={() => setConfirming(false)}>Edit email</button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}


