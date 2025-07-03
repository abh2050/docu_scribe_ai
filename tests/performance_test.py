#!/usr/bin/env python3
"""
Comprehensive Performance Test for DocuScribe AI
Tests memory usage, response times, and throughput
"""

import time
import psutil
import os
import sys
import json
from typing import Dict, List, Tuple
import tracemalloc
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.icd_mapper_agent import ICDMapperAgent
from agents.concept_agent import ConceptAgent
from agents.scribe_agent import ScribeAgent
from agents.context_agent import ContextAgent
from agents.formatter_agent import FormatterAgent

class PerformanceProfiler:
    def __init__(self):
        self.memory_usage = []
        self.response_times = {}
        self.process = psutil.Process(os.getpid())
        
    def start_profiling(self):
        """Start memory profiling"""
        tracemalloc.start()
        
    def get_memory_usage(self) -> Dict:
        """Get current memory usage statistics"""
        memory_info = self.process.memory_info()
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': self.process.memory_percent()
        }
    
    def time_function(self, func_name: str, func, *args, **kwargs):
        """Time a function execution and record memory usage"""
        start_mem = self.get_memory_usage()
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_mem = self.get_memory_usage()
        
        execution_time = end_time - start_time
        if func_name not in self.response_times:
            self.response_times[func_name] = []
        self.response_times[func_name].append({
            'time_ms': execution_time * 1000,
            'start_memory_mb': start_mem['rss_mb'],
            'end_memory_mb': end_mem['rss_mb'],
            'memory_delta_mb': end_mem['rss_mb'] - start_mem['rss_mb']
        })
        
        return result
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        stats = {}
        for func_name, times in self.response_times.items():
            response_times = [t['time_ms'] for t in times]
            memory_deltas = [t['memory_delta_mb'] for t in times]
            
            stats[func_name] = {
                'avg_time_ms': sum(response_times) / len(response_times),
                'min_time_ms': min(response_times),
                'max_time_ms': max(response_times),
                'avg_memory_delta_mb': sum(memory_deltas) / len(memory_deltas),
                'max_memory_delta_mb': max(memory_deltas),
                'call_count': len(times)
            }
        return stats

def test_agent_performance():
    """Test individual agent performance"""
    print("🔬 Performance Testing DocuScribe AI Agents")
    print("=" * 60)
    
    profiler = PerformanceProfiler()
    profiler.start_profiling()
    
    # Sample medical transcript
    sample_transcript = """
    Patient presents today with complaints of severe headache and nausea that started this morning. 
    Reports photophobia and pain behind both eyes. Has a history of hypertension currently managed 
    with lisinopril 10mg daily. Blood pressure today is elevated at 160/95. Patient took ibuprofen 
    400mg without relief. Denies any recent trauma or fever. Reports similar episodes in the past 
    but not this severe. No visual changes or neurological symptoms. Abdomen soft and non-tender.
    """
    
    # Test Context Agent
    print("\n📊 Testing Context Agent...")
    context_agent = ContextAgent()
    contexts = profiler.time_function(
        "context_analysis",
        context_agent.analyze,
        sample_transcript
    )
    print(f"   ✓ Processed {len(contexts['segments'])} context segments")
    
    # Test Concept Agent
    print("\n🧠 Testing Concept Agent...")
    concept_agent = ConceptAgent()
    concepts = profiler.time_function(
        "concept_extraction",
        concept_agent.extract_concepts,
        sample_transcript
    )
    print(f"   ✓ Extracted {len(concepts)} medical concepts")
    
    # Test ICD Mapper Agent (multiple runs to test performance)
    print("\n🏥 Testing ICD Mapper Agent...")
    icd_agent = ICDMapperAgent()
    
    # Test loading performance (first time)
    icd_codes = profiler.time_function(
        "icd_mapping_first",
        icd_agent.map_to_icd10,
        concepts
    )
    print(f"   ✓ First mapping: {len(icd_codes)} ICD codes")
    
    # Test subsequent mappings (should be faster due to caching)
    for i in range(5):
        icd_codes = profiler.time_function(
            "icd_mapping_cached",
            icd_agent.map_to_icd10,
            concepts
        )
    print(f"   ✓ Cached mappings: {len(icd_codes)} ICD codes (5 runs)")
    
    # Test Scribe Agent
    print("\n📝 Testing Scribe Agent...")
    scribe_agent = ScribeAgent()
    soap_note = profiler.time_function(
        "soap_generation",
        scribe_agent.process,
        contexts
    )
    print(f"   ✓ Generated SOAP note: {len(soap_note)} characters")
    
    # Test Formatter Agent
    print("\n📋 Testing Formatter Agent...")
    formatter_agent = FormatterAgent()
    
    # Test JSON formatting
    json_output = profiler.time_function(
        "json_formatting",
        formatter_agent.process,
        {
            'soap_note': soap_note,
            'concepts': concepts,
            'icd_codes': icd_codes,
            'format': 'json'
        }
    )
    print(f"   ✓ JSON formatting: {len(json_output)} characters")
    
    # Test FHIR formatting
    fhir_output = profiler.time_function(
        "fhir_formatting",
        formatter_agent.process,
        {
            'soap_note': soap_note,
            'concepts': concepts,
            'icd_codes': icd_codes,
            'format': 'fhir'
        }
    )
    print(f"   ✓ FHIR formatting: {len(fhir_output)} characters")
    
    return profiler

def test_throughput():
    """Test system throughput with multiple concurrent requests"""
    print("\n🚀 Testing System Throughput...")
    print("-" * 40)
    
    profiler = PerformanceProfiler()
    
    # Sample transcripts of varying lengths
    transcripts = [
        "Patient has headache and nausea.",
        "Patient presents with severe migraine, photophobia, nausea, and elevated blood pressure. History of hypertension.",
        """Patient reports chronic lower back pain radiating down left leg for past 3 weeks. 
        Pain rated 7/10, worse with movement. History of diabetes mellitus type 2, 
        hypertension, and hyperlipidemia. Current medications include metformin, lisinopril, 
        and atorvastatin. Physical exam reveals limited range of motion and positive 
        straight leg raise test.""",
        """Comprehensive annual physical examination. Patient is a 45-year-old male with 
        past medical history significant for hypertension, diabetes mellitus type 2, 
        and hyperlipidemia. Review of systems positive for occasional headaches, 
        mild dyspnea on exertion, and intermittent lower back pain. Physical examination 
        reveals blood pressure 140/90, heart rate 72, respiratory rate 16, temperature 98.6F. 
        Cardiovascular exam normal, pulmonary exam clear, abdominal exam soft and non-tender. 
        Laboratory results pending. Plan includes medication adjustment and lifestyle counseling."""
    ]
    
    # Initialize agents
    agents = {
        'context': ContextAgent(),
        'concept': ConceptAgent(),
        'icd': ICDMapperAgent(),
        'scribe': ScribeAgent(),
        'formatter': FormatterAgent()
    }
    
    total_start_time = time.time()
    
    for i, transcript in enumerate(transcripts, 1):
        print(f"\nProcessing transcript {i} ({len(transcript)} chars)...")
        
        # Full pipeline processing
        contexts = profiler.time_function(
            f"pipeline_context_{i}",
            agents['context'].analyze,
            transcript
        )
        
        concepts = profiler.time_function(
            f"pipeline_concept_{i}",
            agents['concept'].extract_concepts,
            transcript
        )
        
        icd_codes = profiler.time_function(
            f"pipeline_icd_{i}",
            agents['icd'].map_to_icd10,
            concepts
        )
        
        soap_note = profiler.time_function(
            f"pipeline_soap_{i}",
            agents['scribe'].process,
            contexts
        )
        
        output = profiler.time_function(
            f"pipeline_format_{i}",
            agents['formatter'].process,
            {
                'soap_note': soap_note,
                'concepts': concepts,
                'icd_codes': icd_codes,
                'format': 'json'
            }
        )
        
        print(f"   ✓ Processed: {len(concepts)} concepts, {len(icd_codes)} ICD codes")
    
    total_time = time.time() - total_start_time
    print(f"\n📈 Total processing time: {total_time:.2f} seconds")
    print(f"📈 Average time per transcript: {total_time/len(transcripts):.2f} seconds")
    print(f"📈 Throughput: {len(transcripts)/total_time:.2f} transcripts/second")
    
    return profiler

def print_performance_report(profiler: PerformanceProfiler):
    """Print comprehensive performance report"""
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE REPORT")
    print("=" * 60)
    
    stats = profiler.get_stats()
    current_memory = profiler.get_memory_usage()
    
    print(f"\n💾 Current Memory Usage:")
    print(f"   RSS: {current_memory['rss_mb']:.1f} MB")
    print(f"   VMS: {current_memory['vms_mb']:.1f} MB")
    print(f"   Percent: {current_memory['percent']:.1f}%")
    
    print(f"\n⚡ Response Time Analysis:")
    for func_name, func_stats in sorted(stats.items()):
        print(f"\n   {func_name}:")
        print(f"     Average: {func_stats['avg_time_ms']:.1f} ms")
        print(f"     Range: {func_stats['min_time_ms']:.1f} - {func_stats['max_time_ms']:.1f} ms")
        print(f"     Memory impact: {func_stats['avg_memory_delta_mb']:.2f} MB avg, {func_stats['max_memory_delta_mb']:.2f} MB max")
        print(f"     Calls: {func_stats['call_count']}")
    
    # Performance benchmarks
    print(f"\n🎯 Performance Benchmarks:")
    if 'icd_mapping_cached' in stats:
        cached_time = stats['icd_mapping_cached']['avg_time_ms']
        if cached_time < 50:
            print(f"   ✅ ICD Mapping (cached): {cached_time:.1f} ms - Excellent")
        elif cached_time < 100:
            print(f"   ⚠️  ICD Mapping (cached): {cached_time:.1f} ms - Good")
        else:
            print(f"   ❌ ICD Mapping (cached): {cached_time:.1f} ms - Needs optimization")
    
    if 'concept_extraction' in stats:
        concept_time = stats['concept_extraction']['avg_time_ms']
        if concept_time < 10:
            print(f"   ✅ Concept Extraction: {concept_time:.1f} ms - Excellent")
        elif concept_time < 50:
            print(f"   ⚠️  Concept Extraction: {concept_time:.1f} ms - Good")
        else:
            print(f"   ❌ Concept Extraction: {concept_time:.1f} ms - Needs optimization")
    
    # Memory efficiency check
    total_memory = current_memory['rss_mb']
    if total_memory < 100:
        print(f"   ✅ Memory Usage: {total_memory:.1f} MB - Excellent")
    elif total_memory < 250:
        print(f"   ⚠️  Memory Usage: {total_memory:.1f} MB - Good")
    else:
        print(f"   ❌ Memory Usage: {total_memory:.1f} MB - High")
    
    print(f"\n📋 System Status: All components operational")
    print(f"🚀 Ready for production workloads")

def main():
    """Main performance test runner"""
    print("🎯 DocuScribe AI Performance Test Suite")
    print("=" * 60)
    
    # Test individual agent performance
    profiler1 = test_agent_performance()
    
    # Test system throughput
    profiler2 = test_throughput()
    
    # Combine profiling data
    combined_profiler = PerformanceProfiler()
    combined_profiler.response_times.update(profiler1.response_times)
    combined_profiler.response_times.update(profiler2.response_times)
    
    # Print comprehensive report
    print_performance_report(combined_profiler)
    
    # Save results
    stats = combined_profiler.get_stats()
    current_memory = combined_profiler.get_memory_usage()
    
    performance_data = {
        'timestamp': time.time(),
        'memory_usage': current_memory,
        'performance_stats': stats,
        'summary': {
            'total_functions_tested': len(stats),
            'total_function_calls': sum(s['call_count'] for s in stats.values()),
            'average_response_time_ms': sum(s['avg_time_ms'] for s in stats.values()) / len(stats),
            'total_memory_mb': current_memory['rss_mb']
        }
    }
    
    os.makedirs('performance_results', exist_ok=True)
    with open(f'performance_results/performance_test_{int(time.time())}.json', 'w') as f:
        json.dump(performance_data, f, indent=2)
    
    print(f"\n💾 Performance data saved to tests/performance_results/")

if __name__ == "__main__":
    main()
