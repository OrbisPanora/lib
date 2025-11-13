from collections import OrderedDict
from typing import Optional, Tuple, Any
import threading


class CacheManager:
    """
    LRU Cache Manager for Minecraft chunks and regions.
    Thread-safe implementation with configurable size limits.
    
    Attributes
    ----------
    max_size : int
        Maximum number of items to keep in cache
    cache : OrderedDict
        Ordered dictionary storing cached items
    hits : int
        Number of cache hits
    misses : int
        Number of cache misses
    """
    
    def __init__(self, max_size: int = 256):
        """
        Initialize the cache manager.
        
        Parameters
        ----------
        max_size : int
            Maximum number of items to cache (default: 256)
        """
        self.max_size = max_size
        self.cache: OrderedDict[Tuple, Any] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self._lock = threading.Lock()
    
    def get(self, key: Tuple) -> Optional[Any]:
        """
        Get an item from cache.
        
        Parameters
        ----------
        key : Tuple
            Cache key (e.g., (region_x, region_z, chunk_x, chunk_z))
        
        Returns
        -------
        Optional[Any]
            Cached item if found, None otherwise
        """
        with self._lock:
            if key in self.cache:
                # Move to end to mark as recently used (LRU)
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            
            self.misses += 1
            return None
    
    def put(self, key: Tuple, value: Any) -> None:
        """
        Put an item in cache.
        
        Parameters
        ----------
        key : Tuple
            Cache key
        value : Any
            Value to cache
        """
        with self._lock:
            if key in self.cache:
                # Update existing entry and mark as recently used
                self.cache.move_to_end(key)
                self.cache[key] = value
            else:
                self.cache[key] = value
                
                # Evict least recently used item if cache is full
                if len(self.cache) > self.max_size:
                    self.cache.popitem(last=False)
    
    def invalidate(self, key: Tuple) -> None:
        """
        Remove an item from cache.
        
        Parameters
        ----------
        key : Tuple
            Cache key to invalidate
        """
        with self._lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self) -> None:
        """Clear all cached items."""
        with self._lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns
        -------
        dict
            Dictionary with cache statistics
        """
        with self._lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': f"{hit_rate:.2f}%",
                'total_requests': total
            }
    
    def resize(self, new_max_size: int) -> None:
        """
        Resize the cache.
        
        Parameters
        ----------
        new_max_size : int
            New maximum cache size
        """
        with self._lock:
            self.max_size = new_max_size
            
            while len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
    
    def __len__(self) -> int:
        """Return current cache size."""
        return len(self.cache)
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return (f"CacheManager(size={stats['size']}/{stats['max_size']}, "
                f"hits={stats['hits']}, misses={stats['misses']}, "
                f"hit_rate={stats['hit_rate']})")
