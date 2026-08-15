import * as React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
}

export const Progress = ({ value, className, ...props }: ProgressProps) => {
  const percentage = Math.min(Math.max(value, 0), 100);

  return (
    <div
      className={twMerge(clsx('w-full bg-slate-800 rounded-full h-2 overflow-hidden', className))}
      {...props}
    >
      <div
        className="bg-indigo-500 h-full transition-all duration-300 ease-out"
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
};
