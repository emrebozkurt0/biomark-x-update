import React, { useEffect, useState } from 'react';

const InfoPanel = ({ id, title = 'Info', children, defaultOpen = true }) => {
  const storageKey = `infoPanel.${id}.open`;
  const [open, setOpen] = useState(defaultOpen);

  useEffect(() => {
    const saved = sessionStorage.getItem(storageKey);
    if (saved !== null) {
      setOpen(saved === 'true');
    } else {
      setOpen(defaultOpen);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const toggle = () => {
    const next = !open;
    setOpen(next);
    sessionStorage.setItem(storageKey, String(next));
  };

  return (
    <div className="info-panel">
      <button className="info-panel-toggle" onClick={toggle} aria-expanded={open}>
        <span className="info-panel-title">{title}</span>
        <span className="info-panel-caret" aria-hidden>
          {open ? '▾' : '▸'}
        </span>
      </button>
      {open && (
        <div className="info-panel-content">
          {children}
        </div>
      )}
    </div>
  );
};

export default InfoPanel;


