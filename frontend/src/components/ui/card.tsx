import * as React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const Card = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={twMerge(
      clsx(
        'bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl p-6 shadow-xl',
        className
      )
    )}
    {...props}
  >
    {children}
  </div>
);

export const CardHeader = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={twMerge(clsx('mb-4 border-b border-slate-800/80 pb-4', className))} {...props}>
    {children}
  </div>
);

export const CardTitle = ({ className, children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
  <h3 className={twMerge(clsx('text-lg font-semibold text-slate-100 tracking-tight', className))} {...props}>
    {children}
  </h3>
);
