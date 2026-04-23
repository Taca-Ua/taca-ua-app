
type maxWidthOptions = 'sm' | 'md' | 'lg' | 'xl';
type minWidthOptions = 'sm' | 'md' | 'lg' | 'xl';

const BaseModal = ({ children, maxWidth, minWidth } : { children: React.ReactNode; maxWidth?: maxWidthOptions; minWidth?: minWidthOptions }) => {

  return (
    <div className=`bg-white rounded-lg p-8 w-full min-w-[500px] max-w-md`>
        {children}
    </div>
  );
};

export default BaseModal
