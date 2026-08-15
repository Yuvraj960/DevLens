'use client';

import React, { useState } from 'react';
import { Folder, FolderOpen, FileCode, FileText, ChevronRight, ChevronDown } from 'lucide-react';
import type { FileTreeNode } from '@/types/api';

interface FileTreeProps {
  nodes: FileTreeNode[];
  onSelectFile?: (path: string) => void;
}

const TreeNodeItem: React.FC<{
  node: FileTreeNode;
  onSelectFile?: (path: string) => void;
  level: number;
}> = ({ node, onSelectFile, level }) => {
  const [isOpen, setIsOpen] = useState(level < 1);

  const toggle = () => {
    if (node.is_directory) {
      setIsOpen(!isOpen);
    } else if (onSelectFile) {
      onSelectFile(node.path);
    }
  };

  return (
    <div className="select-none">
      <div
        onClick={toggle}
        style={{ paddingLeft: `${level * 16 + 12}px` }}
        className={`flex items-center gap-2 py-1.5 px-2 hover:bg-slate-800/60 rounded-md cursor-pointer text-xs transition-colors ${
          node.is_directory ? 'text-slate-200 font-medium' : 'text-slate-400 hover:text-slate-100'
        }`}
      >
        {node.is_directory ? (
          <>
            {isOpen ? <ChevronDown className="w-3.5 h-3.5 text-slate-500" /> : <ChevronRight className="w-3.5 h-3.5 text-slate-500" />}
            {isOpen ? <FolderOpen className="w-4 h-4 text-indigo-400" /> : <Folder className="w-4 h-4 text-indigo-400/80" />}
          </>
        ) : (
          <>
            <span className="w-3.5 h-3.5" />
            {node.name.endsWith('.ts') || node.name.endsWith('.tsx') || node.name.endsWith('.py') ? (
              <FileCode className="w-4 h-4 text-slate-400" />
            ) : (
              <FileText className="w-4 h-4 text-slate-500" />
            )}
          </>
        )}

        <span className="truncate">{node.name}</span>

        {!node.is_directory && node.size_bytes !== undefined && (
          <span className="ml-auto text-[10px] text-slate-600 font-mono">
            {node.size_bytes < 1024 ? `${node.size_bytes} B` : `${(node.size_bytes / 1024).toFixed(1)} KB`}
          </span>
        )}
      </div>

      {node.is_directory && isOpen && node.children && (
        <div>
          {node.children.map((child) => (
            <TreeNodeItem
              key={child.path}
              node={child}
              onSelectFile={onSelectFile}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const FileTree: React.FC<FileTreeProps> = ({ nodes, onSelectFile }) => {
  return (
    <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-2 max-h-[600px] overflow-y-auto font-mono">
      {nodes && nodes.length > 0 ? (
        nodes.map((node) => (
          <TreeNodeItem key={node.path} node={node} onSelectFile={onSelectFile} level={0} />
        ))
      ) : (
        <div className="p-4 text-center text-xs text-slate-500">No files found in repository.</div>
      )}
    </div>
  );
};
