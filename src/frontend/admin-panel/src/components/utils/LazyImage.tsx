import { useState } from "react";

// Image component that only requests the image when it shows up in the viewport, and shows a placeholder while loading
const LazyImage = ({ src, alt, className }: { src: string, alt: string, className?: string }) => {
  const [ isInView, setIsInView ] = useState(false);
  const [ isLoaded, setIsLoaded ] = useState(false);

    return (
        <div
            className={className}
            onLoad={() => setIsLoaded(true)}
            ref={(el) => {
                if (el) {
                    const observer = new IntersectionObserver(([entry]) => {
                        if (entry.isIntersecting) {
                            setIsInView(true);
                            observer.disconnect();
                        }
                    });
                    observer.observe(el);
                }
            }}
        >
            {isInView && <img src={src} alt={alt} className={className + (isLoaded ? "" : "hidden")} />}
        </div>
    );
}

export default LazyImage;
