/**
 * Usage example:
 *   import { btn } from '@/styles/buttonStyles';
 *   <button className={`px-4 py-2 rounded-md font-medium transition-colors ${btn.primary}`}>Save</button>
 * To change a color globally, edit only this file.
 */

export const btn = {
  primary: 'bg-teal-500 hover:bg-teal-600 text-white',

  danger: 'bg-red-600 hover:bg-red-700 text-white',

  dangerLight: 'bg-red-500 hover:bg-red-600 text-white',

  dangerGhost: 'bg-red-100 hover:bg-red-200 text-red-700',

  secondary: 'bg-gray-300 hover:bg-gray-400 text-gray-800',

  secondaryAlt: 'bg-gray-200 hover:bg-gray-300 text-gray-700',

  info: 'bg-blue-500 hover:bg-blue-600 text-white',

  infoStrong: 'bg-blue-600 hover:bg-blue-700 text-white',

  success: 'bg-green-600 hover:bg-green-700 text-white',
} as const;

export type BtnVariant = keyof typeof btn;
