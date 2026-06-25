import { useRef } from "react";

const AboutUsEditableText = ({
  aboutUsTextLinesState
} : {
  aboutUsTextLinesState: [string[], React.Dispatch<React.SetStateAction<string[]>>]
}) => {
    const [aboutUsTextLines, setAboutUsTextLines] = aboutUsTextLinesState;
    const textAreaRef = useRef<HTMLDivElement>(null);

    const addNewLine = (index: number) => {
        const updatedLines = [...aboutUsTextLines];
        updatedLines.splice(index + 1, 0, "");
        setAboutUsTextLines(updatedLines);
    }

    const removeLine = (index: number) => {
        const updatedLines = [...aboutUsTextLines];
        updatedLines.splice(index, 1);
        setAboutUsTextLines(updatedLines);
    }

    const saveAboutUsTextLine = (index: number, newText: string) => {
        setAboutUsTextLines(prev => {
            const updated = [...prev];
            updated[index] = newText;
            return updated;
        });
    }

    return (
      <div
        className="text-xl md:text-2xl text-gray-700 leading-relaxed space-y-8"
        ref={textAreaRef}
      >
        {aboutUsTextLines.map((line, index) => (
          <p
            contentEditable
            suppressContentEditableWarning
            onBlur={(e) =>
              saveAboutUsTextLine(index, e.currentTarget.textContent || "")
            }
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                if (e.shiftKey) {
                  addNewLine(index);
                  // Move focus to the new line
                  setTimeout(() => {
                    const nextLine: any =
                      textAreaRef.current?.querySelectorAll(
                        "p[contenteditable]",
                      )[index + 1];
                    if (nextLine) {
                      nextLine.focus();
                    }
                  }, 0);
                }
              }
              if (e.key === "Backspace" && e.currentTarget.textContent === "") {
                e.preventDefault();
                removeLine(index);
                // Move focus to the previous line if it exists
                setTimeout(() => {
                  const prevLine: any =
                    textAreaRef.current?.querySelectorAll("p[contenteditable]")[
                      index - 1
                    ];
                  if (prevLine) {
                    prevLine.focus();
                  }
                }, 0);
              }
            }}
            key={index}
            className="border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {line}
          </p>
        ))}
      </div>
    );
};

export default AboutUsEditableText;
