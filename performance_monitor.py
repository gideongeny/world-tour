#!/usr/bin/env python3
"""
World Tour Performance Monitor
Monitors website performance and generates reports
"""

import requests
import time
import json
import sqlite3
from datetime import datetime, timedelta
import os

class PerformanceMonitor:
    def __init__(self, base_url="https://world-tour-1.onrender.com"):
        self.base_url = base_url
        self.db_path = "instance/performance_metrics.db"
        self.init_database()
    
    def init_database(self):
        """Initialize performance metrics database"""
        os.makedirs("instance", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                response_time REAL NOT NULL,
                status_code INTEGER,
                content_size INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                error_type TEXT,
                error_message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def test_endpoint(self, endpoint="/"):
        """Test a specific endpoint and record metrics"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=30)
            response_time = time.time() - start_time
            
            # Record metrics
            self.record_metric(url, response_time, response.status_code, len(response.content))
            
            return {
                'url': url,
                'response_time': response_time,
                'status_code': response.status_code,
                'content_size': len(response.content),
                'success': response.status_code == 200
            }
            
        except Exception as e:
            self.record_error(url, type(e).__name__, str(e))
            return {
                'url': url,
                'error': str(e),
                'success': False
            }
    
    def record_metric(self, url, response_time, status_code, content_size):
        """Record performance metric in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_metrics (url, response_time, status_code, content_size)
            VALUES (?, ?, ?, ?)
        ''', (url, response_time, status_code, content_size))
        
        conn.commit()
        conn.close()
    
    def record_error(self, url, error_type, error_message):
        """Record error in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO error_logs (url, error_type, error_message)
            VALUES (?, ?, ?)
        ''', (url, error_type, error_message))
        
        conn.commit()
        conn.close()
    
    def run_performance_test(self):
        """Run comprehensive performance test"""
        print("🚀 Starting Performance Test...")
        print("=" * 50)
        
        endpoints = [
            "/",
            "/travel",
            "/destinations",
            "/flights",
            "/hotels",
            "/packages",
            "/blog",
            "/contact",
            "/offers"
        ]
        
        results = []
        total_time = 0
        
        for endpoint in endpoints:
            print(f"Testing {endpoint}...")
            result = self.test_endpoint(endpoint)
            results.append(result)
            
            if result['success']:
                total_time += result['response_time']
                print(f"  ✓ {result['response_time']:.3f}s ({result['content_size']} bytes)")
            else:
                print(f"  ✗ Error: {result.get('error', 'Unknown error')}")
        
        # Calculate averages
        successful_tests = [r for r in results if r['success']]
        if successful_tests:
            avg_response_time = sum(r['response_time'] for r in successful_tests) / len(successful_tests)
            avg_content_size = sum(r['content_size'] for r in successful_tests) / len(successful_tests)
            
            print("\n📊 Performance Summary:")
            print(f"  Average Response Time: {avg_response_time:.3f}s")
            print(f"  Average Content Size: {avg_content_size:.0f} bytes")
            print(f"  Success Rate: {len(successful_tests)}/{len(results)} ({len(successful_tests)/len(results)*100:.1f}%)")
        
        return results
    
    def generate_report(self, days=7):
        """Generate performance report for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get metrics from last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT url, AVG(response_time), AVG(content_size), COUNT(*), 
                   MIN(response_time), MAX(response_time)
            FROM performance_metrics 
            WHERE timestamp > ?
            GROUP BY url
            ORDER BY AVG(response_time) DESC
        ''', (cutoff_date,))
        
        metrics = cursor.fetchall()
        
        cursor.execute('''
            SELECT error_type, COUNT(*) 
            FROM error_logs 
            WHERE timestamp > ?
            GROUP BY error_type
            ORDER BY COUNT(*) DESC
        ''', (cutoff_date,))
        
        errors = cursor.fetchall()
        
        conn.close()
        
        print(f"\n📈 Performance Report (Last {days} days)")
        print("=" * 50)
        
        if metrics:
            print("\n🏆 Top 5 Slowest Endpoints:")
            for i, (url, avg_time, avg_size, count, min_time, max_time) in enumerate(metrics[:5], 1):
                print(f"  {i}. {url}")
                print(f"     Avg: {avg_time:.3f}s | Min: {min_time:.3f}s | Max: {max_time:.3f}s")
                print(f"     Size: {avg_size:.0f} bytes | Tests: {count}")
        
        if errors:
            print("\n⚠️  Error Summary:")
            for error_type, count in errors:
                print(f"  {error_type}: {count} occurrences")
        
        return {
            'metrics': metrics,
            'errors': errors
        }
    
    def check_optimization_opportunities(self):
        """Identify optimization opportunities"""
        print("\n🔍 Optimization Opportunities:")
        print("=" * 50)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for slow endpoints
        cursor.execute('''
            SELECT url, AVG(response_time), COUNT(*)
            FROM performance_metrics 
            WHERE timestamp > datetime('now', '-1 day')
            GROUP BY url
            HAVING AVG(response_time) > 2.0
            ORDER BY AVG(response_time) DESC
        ''')
        
        slow_endpoints = cursor.fetchall()
        
        if slow_endpoints:
            print("\n🐌 Slow Endpoints (>2s average):")
            for url, avg_time, count in slow_endpoints:
                print(f"  • {url}: {avg_time:.3f}s ({count} tests)")
                print("    → Consider: Database optimization, caching, CDN")
        
        # Check for large content
        cursor.execute('''
            SELECT url, AVG(content_size), COUNT(*)
            FROM performance_metrics 
            WHERE timestamp > datetime('now', '-1 day')
            GROUP BY url
            HAVING AVG(content_size) > 500000
            ORDER BY AVG(content_size) DESC
        ''')
        
        large_content = cursor.fetchall()
        
        if large_content:
            print("\n📦 Large Content (>500KB average):")
            for url, avg_size, count in large_content:
                print(f"  • {url}: {avg_size/1024:.1f}KB ({count} tests)")
                print("    → Consider: Image optimization, lazy loading, compression")
        
        # Check error patterns
        cursor.execute('''
            SELECT error_type, COUNT(*)
            FROM error_logs 
            WHERE timestamp > datetime('now', '-1 day')
            GROUP BY error_type
            HAVING COUNT(*) > 5
            ORDER BY COUNT(*) DESC
        ''')
        
        frequent_errors = cursor.fetchall()
        
        if frequent_errors:
            print("\n❌ Frequent Errors (>5 occurrences):")
            for error_type, count in frequent_errors:
                print(f"  • {error_type}: {count} occurrences")
                print("    → Consider: Error handling, monitoring, alerts")
        
        conn.close()
        
        if not slow_endpoints and not large_content and not frequent_errors:
            print("  ✅ No major optimization opportunities identified!")
            print("  Your website is performing well!")

def main():
    monitor = PerformanceMonitor()
    
    # Run performance test
    monitor.run_performance_test()
    
    # Generate report
    monitor.generate_report(days=1)
    
    # Check optimization opportunities
    monitor.check_optimization_opportunities()

if __name__ == "__main__":
    main() 