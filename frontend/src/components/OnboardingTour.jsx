import { useState, useEffect } from 'react';
// eslint-disable-next-line no-unused-vars
import { motion, AnimatePresence } from 'framer-motion';
import { XMarkIcon } from '@heroicons/react/24/outline';

const OnboardingTour = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  
  const steps = [
    {
      title: 'Welcome to Project Sentinel',
      content: 'Your secure-by-design DevSecOps framework. Let\'s get started!',
      target: null,
    },
    {
      title: 'Threat Modeling',
      content: 'Use STRIDE/DREAD methodology to analyze and mitigate security threats.',
      target: 'threats-link',
    },
    {
      title: 'Requirements Management',
      content: 'Manage requirements with enforced security controls mapping.',
      target: 'requirements-link',
    },
    {
      title: 'CI/CD Dashboard',
      content: 'Monitor your security pipeline with real-time vulnerability tracking.',
      target: 'dashboard-link',
    },
  ];
  
  useEffect(() => {
    // Check if user has seen tour
    const hasSeenTour = localStorage.getItem('hasSeenTour');
    if (!hasSeenTour) {
      setIsVisible(true);
    }
  }, []);
  
  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleFinish();
    }
  };
  
  const handleFinish = () => {
    setIsVisible(false);
    localStorage.setItem('hasSeenTour', 'true');
  };
  
  if (!isVisible) return null;
  
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
        onClick={handleFinish}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="card max-w-md relative"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={handleFinish}
            className="absolute top-4 right-4 text-gray-400 hover:text-white"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
          
          <h2 className="text-2xl font-bold text-cyber-blue mb-2">
            {steps[currentStep].title}
          </h2>
          <p className="text-gray-300 mb-6">{steps[currentStep].content}</p>
          
          <div className="flex justify-between items-center">
            <div className="flex gap-2">
              {steps.map((_, index) => (
                <div
                  key={index}
                  className={`h-2 w-2 rounded-full ${
                    index === currentStep ? 'bg-cyber-blue' : 'bg-gray-600'
                  }`}
                />
              ))}
            </div>
            
            <div className="flex gap-2">
              {currentStep > 0 && (
                <button
                  onClick={() => setCurrentStep(currentStep - 1)}
                  className="px-4 py-2 text-gray-400 hover:text-white"
                >
                  Previous
                </button>
              )}
              <button
                onClick={currentStep === steps.length - 1 ? handleFinish : handleNext}
                className="btn-primary"
              >
                {currentStep === steps.length - 1 ? 'Get Started' : 'Next'}
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default OnboardingTour;

