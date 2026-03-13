import { useId, useRef, useState, useCallback } from 'react';
import { createPortal } from 'react-dom';

interface HelpTooltipProps {
  text: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

const GAP = 8; // px between button and tooltip

function computeStyle(
  rect: DOMRect,
  position: NonNullable<HelpTooltipProps['position']>,
  tooltipW = 224, // w-56 = 14rem = 224px
  tooltipH = 60,  // approximate height
): React.CSSProperties {
  switch (position) {
    case 'top':
      return {
        top: rect.top - tooltipH - GAP,
        left: rect.left + rect.width / 2 - tooltipW / 2,
      };
    case 'bottom':
      return {
        top: rect.bottom + GAP,
        left: rect.left + rect.width / 2 - tooltipW / 2,
      };
    case 'left':
      return {
        top: rect.top + rect.height / 2 - tooltipH / 2,
        left: rect.left - tooltipW - GAP,
      };
    case 'right':
      return {
        top: rect.top + rect.height / 2 - tooltipH / 2,
        left: rect.right + GAP,
      };
  }
}

const arrowClasses: Record<NonNullable<HelpTooltipProps['position']>, string> = {
  top:    'top-full  left-1/2 -translate-x-1/2 border-t-gray-700 border-x-transparent border-b-transparent border-4',
  bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-gray-700 border-x-transparent border-t-transparent border-4',
  left:   'left-full  top-1/2 -translate-y-1/2 border-l-gray-700 border-y-transparent border-r-transparent border-4',
  right:  'right-full top-1/2 -translate-y-1/2 border-r-gray-700 border-y-transparent border-l-transparent border-4',
};

export default function HelpTooltip({ text, position = 'top', className = '' }: HelpTooltipProps) {
  const id = useId();
  const btnRef = useRef<HTMLButtonElement>(null);
  const [visible, setVisible] = useState(false);
  const [style, setStyle] = useState<React.CSSProperties>({});

  const show = useCallback(() => {
    if (btnRef.current) {
      setStyle(computeStyle(btnRef.current.getBoundingClientRect(), position));
    }
    setVisible(true);
  }, [position]);

  const hide = useCallback(() => setVisible(false), []);

  return (
    <span className={`relative inline-flex items-center ${className}`}>
      <button
        ref={btnRef}
        type="button"
        aria-describedby={id}
        onMouseEnter={show}
        onMouseLeave={hide}
        onFocus={show}
        onBlur={hide}
        className="w-4 h-4 rounded-full bg-gray-300 hover:bg-teal-500 text-gray-700 hover:text-white text-[10px] font-bold leading-none flex items-center justify-center transition-colors focus:outline-none focus:ring-2 focus:ring-teal-400 cursor-help"
      >
        ?
      </button>

      {createPortal(
        <span
          id={id}
          role="tooltip"
          style={{ position: 'fixed', width: '14rem', ...style }}
          className={`
            pointer-events-none z-[9999] rounded-md bg-gray-700 px-3 py-2
            text-xs text-white shadow-lg
            transition-opacity duration-150
            ${visible ? 'opacity-100' : 'opacity-0'}
          `}
        >
          {text}
          <span className={`absolute w-0 h-0 ${arrowClasses[position]}`} aria-hidden="true" />
        </span>,
        document.body,
      )}
    </span>
  );
}
