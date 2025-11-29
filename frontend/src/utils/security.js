/**
 * Security utilities for input sanitization and output encoding
 */

/**
 * Sanitize user input to prevent XSS attacks
 * @param {string} input - User input string
 * @returns {string} Sanitized string
 */
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') {
    return String(input);
  }
  
  // Remove potentially dangerous characters
  const dangerousChars = ['<', '>', '"', "'", '&', '\x00'];
  let sanitized = input;
  
  dangerousChars.forEach((char) => {
    sanitized = sanitized.replace(new RegExp(char, 'g'), '');
  });
  
  return sanitized.trim();
};

/**
 * Encode output to prevent XSS attacks
 * @param {string} text - Text to encode
 * @returns {string} Encoded text
 */
export const encodeOutput = (text) => {
  if (typeof text !== 'string') {
    text = String(text);
  }
  
  const replacements = {
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '&': '&amp;',
  };
  
  let encoded = text;
  Object.entries(replacements).forEach(([char, entity]) => {
    encoded = encoded.replace(new RegExp(char, 'g'), entity);
  });
  
  return encoded;
};

/**
 * Secure localStorage handling with auto-expire
 */
export const secureStorage = {
  set: (key, value, expireMinutes = 30) => {
    const item = {
      value,
      expiry: new Date().getTime() + expireMinutes * 60 * 1000,
    };
    localStorage.setItem(key, JSON.stringify(item));
  },
  
  get: (key) => {
    const itemStr = localStorage.getItem(key);
    if (!itemStr) {
      return null;
    }
    
    try {
      const item = JSON.parse(itemStr);
      const now = new Date().getTime();
      
      if (now > item.expiry) {
        localStorage.removeItem(key);
        return null;
      }
      
      return item.value;
    } catch {
      localStorage.removeItem(key);
      return null;
    }
  },
  
  remove: (key) => {
    localStorage.removeItem(key);
  },
};

