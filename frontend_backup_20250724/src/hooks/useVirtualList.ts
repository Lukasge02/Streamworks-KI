import { useState, useCallback, useMemo } from 'react';

interface VirtualListOptions {
  itemHeight: number | ((index: number) => number);
  containerHeight: number;
  overscan?: number;
  scrollingDelay?: number;
}

interface VirtualListReturn {
  totalHeight: number;
  startIndex: number;
  endIndex: number;
  visibleItems: Array<{
    index: number;
    style: React.CSSProperties;
  }>;
  scrollToIndex: (index: number, align?: 'start' | 'center' | 'end') => void;
}

/**
 * Virtual list hook for rendering large datasets efficiently
 */
export function useVirtualList<T>(
  items: T[],
  options: VirtualListOptions
): VirtualListReturn {
  const {
    itemHeight,
    containerHeight,
    overscan = 5
  } = options;

  const [scrollTop, setScrollTop] = useState(0);

  const getItemHeight = useCallback((index: number): number => {
    return typeof itemHeight === 'function' ? itemHeight(index) : itemHeight;
  }, [itemHeight]);

  const totalHeight = useMemo(() => {
    if (typeof itemHeight === 'number') {
      return items.length * itemHeight;
    }
    return items.reduce((acc, _, index) => acc + getItemHeight(index), 0);
  }, [items.length, itemHeight, getItemHeight]);

  const getItemOffset = useCallback((index: number): number => {
    if (typeof itemHeight === 'number') {
      return index * itemHeight;
    }
    let offset = 0;
    for (let i = 0; i < index; i++) {
      offset += getItemHeight(i);
    }
    return offset;
  }, [itemHeight, getItemHeight]);

  const findStartIndex = useCallback((scrollTop: number): number => {
    if (typeof itemHeight === 'number') {
      return Math.floor(scrollTop / itemHeight);
    }
    
    let totalOffset = 0;
    for (let i = 0; i < items.length; i++) {
      if (totalOffset + getItemHeight(i) > scrollTop) {
        return i;
      }
      totalOffset += getItemHeight(i);
    }
    return items.length - 1;
  }, [itemHeight, items.length, getItemHeight]);

  const startIndex = useMemo(() => {
    const index = findStartIndex(scrollTop);
    return Math.max(0, index - overscan);
  }, [findStartIndex, scrollTop, overscan]);

  const endIndex = useMemo(() => {
    let index = startIndex;
    let totalHeight = 0;
    
    while (index < items.length && totalHeight < containerHeight + getItemHeight(index)) {
      totalHeight += getItemHeight(index);
      index++;
    }
    
    return Math.min(items.length - 1, index + overscan);
  }, [startIndex, items.length, containerHeight, getItemHeight, overscan]);

  const visibleItems = useMemo(() => {
    const items = [];
    for (let i = startIndex; i <= endIndex; i++) {
      items.push({
        index: i,
        style: {
          position: 'absolute' as const,
          top: getItemOffset(i),
          height: getItemHeight(i),
          width: '100%',
        },
      });
    }
    return items;
  }, [startIndex, endIndex, getItemOffset, getItemHeight]);

  const scrollToIndex = useCallback((
    index: number,
    align: 'start' | 'center' | 'end' = 'start'
  ) => {
    const itemOffset = getItemOffset(index);
    const itemHeight = getItemHeight(index);
    
    let scrollTo = itemOffset;
    
    if (align === 'center') {
      scrollTo = itemOffset - (containerHeight - itemHeight) / 2;
    } else if (align === 'end') {
      scrollTo = itemOffset - containerHeight + itemHeight;
    }
    
    scrollTo = Math.max(0, Math.min(scrollTo, totalHeight - containerHeight));
    setScrollTop(scrollTo);
  }, [getItemOffset, getItemHeight, containerHeight, totalHeight]);


  return {
    totalHeight,
    startIndex,
    endIndex,
    visibleItems,
    scrollToIndex,
  };
}

/**
 * Virtual grid hook for 2D virtualization
 */
export function useVirtualGrid<T>(
  items: T[],
  options: {
    columnCount: number;
    rowHeight: number | ((rowIndex: number) => number);
    columnWidth: number | ((columnIndex: number) => number);
    containerHeight: number;
    containerWidth: number;
    overscan?: number;
  }
) {
  const {
    columnCount,
    rowHeight,
    columnWidth,
    containerHeight,
    containerWidth,
    overscan = 5
  } = options;

  const [scrollTop, setScrollTop] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  const rowCount = Math.ceil(items.length / columnCount);

  const getRowHeight = useCallback((rowIndex: number): number => {
    return typeof rowHeight === 'function' ? rowHeight(rowIndex) : rowHeight;
  }, [rowHeight]);

  const getColumnWidth = useCallback((columnIndex: number): number => {
    return typeof columnWidth === 'function' ? columnWidth(columnIndex) : columnWidth;
  }, [columnWidth]);

  const totalHeight = useMemo(() => {
    if (typeof rowHeight === 'number') {
      return rowCount * rowHeight;
    }
    return Array.from({ length: rowCount }, (_, i) => getRowHeight(i))
      .reduce((acc, height) => acc + height, 0);
  }, [rowCount, rowHeight, getRowHeight]);

  const totalWidth = useMemo(() => {
    if (typeof columnWidth === 'number') {
      return columnCount * columnWidth;
    }
    return Array.from({ length: columnCount }, (_, i) => getColumnWidth(i))
      .reduce((acc, width) => acc + width, 0);
  }, [columnCount, columnWidth, getColumnWidth]);

  const getRowOffset = useCallback((rowIndex: number): number => {
    if (typeof rowHeight === 'number') {
      return rowIndex * rowHeight;
    }
    let offset = 0;
    for (let i = 0; i < rowIndex; i++) {
      offset += getRowHeight(i);
    }
    return offset;
  }, [rowHeight, getRowHeight]);

  const getColumnOffset = useCallback((columnIndex: number): number => {
    if (typeof columnWidth === 'number') {
      return columnIndex * columnWidth;
    }
    let offset = 0;
    for (let i = 0; i < columnIndex; i++) {
      offset += getColumnWidth(i);
    }
    return offset;
  }, [columnWidth, getColumnWidth]);

  const findStartRowIndex = useCallback((scrollTop: number): number => {
    if (typeof rowHeight === 'number') {
      return Math.floor(scrollTop / rowHeight);
    }
    
    let totalOffset = 0;
    for (let i = 0; i < rowCount; i++) {
      if (totalOffset + getRowHeight(i) > scrollTop) {
        return i;
      }
      totalOffset += getRowHeight(i);
    }
    return rowCount - 1;
  }, [rowHeight, rowCount, getRowHeight]);

  const findStartColumnIndex = useCallback((scrollLeft: number): number => {
    if (typeof columnWidth === 'number') {
      return Math.floor(scrollLeft / columnWidth);
    }
    
    let totalOffset = 0;
    for (let i = 0; i < columnCount; i++) {
      if (totalOffset + getColumnWidth(i) > scrollLeft) {
        return i;
      }
      totalOffset += getColumnWidth(i);
    }
    return columnCount - 1;
  }, [columnWidth, columnCount, getColumnWidth]);

  const startRowIndex = Math.max(0, findStartRowIndex(scrollTop) - overscan);
  const startColumnIndex = Math.max(0, findStartColumnIndex(scrollLeft) - overscan);

  const endRowIndex = useMemo(() => {
    let index = startRowIndex;
    let totalHeight = 0;
    
    while (index < rowCount && totalHeight < containerHeight + getRowHeight(index)) {
      totalHeight += getRowHeight(index);
      index++;
    }
    
    return Math.min(rowCount - 1, index + overscan);
  }, [startRowIndex, rowCount, containerHeight, getRowHeight, overscan]);

  const endColumnIndex = useMemo(() => {
    let index = startColumnIndex;
    let totalWidth = 0;
    
    while (index < columnCount && totalWidth < containerWidth + getColumnWidth(index)) {
      totalWidth += getColumnWidth(index);
      index++;
    }
    
    return Math.min(columnCount - 1, index + overscan);
  }, [startColumnIndex, columnCount, containerWidth, getColumnWidth, overscan]);

  const visibleCells = useMemo(() => {
    const cells = [];
    for (let rowIndex = startRowIndex; rowIndex <= endRowIndex; rowIndex++) {
      for (let columnIndex = startColumnIndex; columnIndex <= endColumnIndex; columnIndex++) {
        const itemIndex = rowIndex * columnCount + columnIndex;
        if (itemIndex < items.length) {
          cells.push({
            rowIndex,
            columnIndex,
            itemIndex,
            style: {
              position: 'absolute' as const,
              top: getRowOffset(rowIndex),
              left: getColumnOffset(columnIndex),
              height: getRowHeight(rowIndex),
              width: getColumnWidth(columnIndex),
            },
          });
        }
      }
    }
    return cells;
  }, [
    startRowIndex,
    endRowIndex,
    startColumnIndex,
    endColumnIndex,
    columnCount,
    items.length,
    getRowOffset,
    getColumnOffset,
    getRowHeight,
    getColumnWidth
  ]);

  const scrollToItem = useCallback((
    itemIndex: number,
    align: 'start' | 'center' | 'end' = 'start'
  ) => {
    const rowIndex = Math.floor(itemIndex / columnCount);
    const columnIndex = itemIndex % columnCount;
    
    const rowOffset = getRowOffset(rowIndex);
    const columnOffset = getColumnOffset(columnIndex);
    
    let scrollToTop = rowOffset;
    let scrollToLeft = columnOffset;
    
    if (align === 'center') {
      scrollToTop = rowOffset - (containerHeight - getRowHeight(rowIndex)) / 2;
      scrollToLeft = columnOffset - (containerWidth - getColumnWidth(columnIndex)) / 2;
    } else if (align === 'end') {
      scrollToTop = rowOffset - containerHeight + getRowHeight(rowIndex);
      scrollToLeft = columnOffset - containerWidth + getColumnWidth(columnIndex);
    }
    
    scrollToTop = Math.max(0, Math.min(scrollToTop, totalHeight - containerHeight));
    scrollToLeft = Math.max(0, Math.min(scrollToLeft, totalWidth - containerWidth));
    
    setScrollTop(scrollToTop);
    setScrollLeft(scrollToLeft);
  }, [
    columnCount,
    getRowOffset,
    getColumnOffset,
    getRowHeight,
    getColumnWidth,
    containerHeight,
    containerWidth,
    totalHeight,
    totalWidth
  ]);

  const handleScroll = useCallback((event: React.UIEvent<HTMLElement>) => {
    setScrollTop(event.currentTarget.scrollTop);
    setScrollLeft(event.currentTarget.scrollLeft);
  }, []);

  return {
    totalHeight,
    totalWidth,
    startRowIndex,
    endRowIndex,
    startColumnIndex,
    endColumnIndex,
    visibleCells,
    scrollToItem,
    handleScroll,
  };
}