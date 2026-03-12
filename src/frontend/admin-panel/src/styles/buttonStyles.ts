/**
 * Usage example:
 *   import { btn } from '@/styles/buttonStyles';
 *   <button className={`px-4 py-2 rounded-md font-medium transition-colors ${btn.primary}`}>Save</button>
 * To change a color globally, edit only this file.
 */

export const btn = {
  primary: 'bg-teal-700 hover:bg-teal-800 text-white',        // 5.47:1 ✓ (was teal-500: 2.49:1)

  danger: 'bg-red-600 hover:bg-red-700 text-white',            // 4.83:1 ✓ unchanged

  dangerLight: 'bg-red-600 hover:bg-red-700 text-white',       // 4.83:1 ✓ (was red-500: 3.76:1)

  dangerGhost: 'bg-red-100 hover:bg-red-200 text-red-700',     // 5.30:1 ✓ unchanged

  secondary: 'bg-gray-300 hover:bg-gray-400 text-gray-800',    // 9.96:1 ✓ unchanged

  secondaryAlt: 'bg-gray-200 hover:bg-gray-300 text-gray-700', // 8.33:1 ✓ unchanged

  info: 'bg-blue-600 hover:bg-blue-700 text-white',            // 5.17:1 ✓ (was blue-500: 3.68:1)

  infoStrong: 'bg-blue-700 hover:bg-blue-800 text-white',      // 6.70:1 ✓ (was blue-600: 5.17:1)

  success: 'bg-green-700 hover:bg-green-800 text-white',       // 5.02:1 ✓ (was green-600: 3.30:1)
} as const;

export type BtnVariant = keyof typeof btn;
