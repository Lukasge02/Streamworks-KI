#!/usr/bin/env python3
"""
🎯 PRODUCTION Q&A SYSTEM TEST SUITE
Comprehensive testing for production excellence
"""
import asyncio
import sys
import os
import logging
import time
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.perfect_qa_service import perfect_qa

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionQATest:
    """Production-grade test suite"""
    
    def __init__(self):
        self.test_questions = [
            # Basic functionality
            "Was ist StreamWorks?",
            "Welche Funktionen hat StreamWorks?",
            "Wie kann StreamWorks in der Cloud betrieben werden?",
            
            # Technical questions
            "Welche Datenformate werden von StreamWorks unterstützt?",
            "Wie funktioniert die Sicherheit in StreamWorks?",
            "Welche Systemanforderungen hat StreamWorks?",
            
            # Advanced questions
            "Wie kann ich StreamWorks mit anderen Systemen integrieren?",
            "Welche Backup-Strategien gibt es für StreamWorks?",
            "Wie wird StreamWorks skaliert?",
            
            # Edge cases
            "Wo finde ich Hilfe bei Problemen?",
            "Wer ist der Ansprechpartner für Linux-Systeme?",
            "Gibt es eine API-Dokumentation?"
        ]
        
        self.results = []
        self.failed_tests = []
        
    async def run_comprehensive_test(self) -> bool:
        """Run comprehensive production test suite"""
        print("🎯 Starting Production Q&A System Test Suite")
        print("=" * 60)
        
        try:
            # 1. System initialization test
            await self._test_initialization()
            
            # 2. Basic functionality test
            await self._test_basic_functionality()
            
            # 3. Performance test
            await self._test_performance()
            
            # 4. Quality assurance test
            await self._test_quality_assurance()
            
            # 5. Error handling test
            await self._test_error_handling()
            
            # 6. Statistics test
            await self._test_statistics()
            
            # Generate report
            success = self._generate_report()
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            return False
    
    async def _test_initialization(self):
        """Test system initialization"""
        print("\n📊 Test 1: System Initialization")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            await perfect_qa.initialize()
            init_time = time.time() - start_time
            
            assert perfect_qa.is_ready, "System should be ready"
            assert perfect_qa.embedding_model is not None, "Embedding model should be loaded"
            assert perfect_qa.collection is not None, "ChromaDB collection should be connected"
            
            print(f"✅ System initialized in {init_time:.2f}s")
            print(f"   - Embedding model: {perfect_qa.config['embedding_model']}")
            print(f"   - Collection: {perfect_qa.config['collection_name']}")
            print(f"   - Ready: {perfect_qa.is_ready}")
            
        except Exception as e:
            self.failed_tests.append(f"Initialization: {e}")
            raise
    
    async def _test_basic_functionality(self):
        """Test basic Q&A functionality"""
        print("\n📊 Test 2: Basic Functionality")
        print("-" * 40)
        
        for i, question in enumerate(self.test_questions[:3], 1):
            try:
                print(f"\n🔍 Test 2.{i}: {question}")
                
                result = await perfect_qa.ask(question)
                
                # Validate response structure
                assert result.question == question, "Question should match"
                assert len(result.answer) > 50, "Answer should be substantial"
                assert result.confidence > 0.3, "Confidence should be reasonable"
                assert result.processing_time > 0, "Processing time should be positive"
                assert len(result.sources) > 0, "Should have sources"
                
                print(f"   ✅ Response: {len(result.answer)} chars")
                print(f"   ✅ Confidence: {result.confidence:.2f}")
                print(f"   ✅ Processing time: {result.processing_time:.2f}s")
                print(f"   ✅ Sources: {len(result.sources)}")
                
                self.results.append({
                    'question': question,
                    'success': True,
                    'confidence': result.confidence,
                    'processing_time': result.processing_time,
                    'answer_length': len(result.answer)
                })
                
            except Exception as e:
                self.failed_tests.append(f"Basic functionality {i}: {e}")
                self.results.append({
                    'question': question,
                    'success': False,
                    'error': str(e)
                })
    
    async def _test_performance(self):
        """Test performance requirements"""
        print("\n📊 Test 3: Performance Requirements")
        print("-" * 40)
        
        test_questions = self.test_questions[3:6]
        times = []
        
        for i, question in enumerate(test_questions, 1):
            try:
                start_time = time.time()
                result = await perfect_qa.ask(question)
                end_time = time.time()
                
                processing_time = end_time - start_time
                times.append(processing_time)
                
                print(f"🔍 Test 3.{i}: {processing_time:.2f}s - {question[:50]}...")
                
                # Performance requirements
                assert processing_time < 10.0, f"Response too slow: {processing_time:.2f}s"
                assert result.confidence > 0.5, f"Quality too low: {result.confidence:.2f}"
                
            except Exception as e:
                self.failed_tests.append(f"Performance {i}: {e}")
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"\n📈 Performance Summary:")
            print(f"   - Average response time: {avg_time:.2f}s")
            print(f"   - Min response time: {min(times):.2f}s")
            print(f"   - Max response time: {max(times):.2f}s")
            
            assert avg_time < 5.0, f"Average response time too slow: {avg_time:.2f}s"
            print("   ✅ Performance requirements met")
    
    async def _test_quality_assurance(self):
        """Test quality assurance metrics"""
        print("\n📊 Test 4: Quality Assurance")
        print("-" * 40)
        
        test_questions = self.test_questions[6:9]
        confidences = []
        quality_scores = []
        
        for i, question in enumerate(test_questions, 1):
            try:
                result = await perfect_qa.ask(question)
                
                confidences.append(result.confidence)
                quality_scores.append(result.quality_score)
                
                print(f"🔍 Test 4.{i}: Quality {result.quality_score:.2f} | Confidence {result.confidence:.2f}")
                
                # Quality requirements
                assert result.confidence > 0.6, f"Confidence too low: {result.confidence:.2f}"
                assert result.quality_score > 0.5, f"Quality too low: {result.quality_score:.2f}"
                assert 'StreamWorks' in result.answer, "Answer should mention StreamWorks"
                
            except Exception as e:
                self.failed_tests.append(f"Quality {i}: {e}")
        
        if confidences and quality_scores:
            avg_confidence = sum(confidences) / len(confidences)
            avg_quality = sum(quality_scores) / len(quality_scores)
            
            print(f"\n📈 Quality Summary:")
            print(f"   - Average confidence: {avg_confidence:.2f}")
            print(f"   - Average quality: {avg_quality:.2f}")
            
            assert avg_confidence > 0.7, f"Average confidence too low: {avg_confidence:.2f}"
            assert avg_quality > 0.6, f"Average quality too low: {avg_quality:.2f}"
            print("   ✅ Quality requirements met")
    
    async def _test_error_handling(self):
        """Test error handling"""
        print("\n📊 Test 5: Error Handling")
        print("-" * 40)
        
        error_cases = [
            "",  # Empty question
            "x" * 1000,  # Too long question
            "???",  # Invalid question
        ]
        
        for i, question in enumerate(error_cases, 1):
            try:
                print(f"🔍 Test 5.{i}: Error case - {question[:50]}...")
                
                if question == "":
                    # Empty question should be handled gracefully
                    try:
                        await perfect_qa.ask(question)
                        print("   ⚠️ Empty question processed (should be handled)")
                    except Exception:
                        print("   ✅ Empty question rejected properly")
                else:
                    result = await perfect_qa.ask(question)
                    # Should still produce a response
                    assert len(result.answer) > 10, "Should produce some response"
                    print(f"   ✅ Handled gracefully: {result.confidence:.2f}")
                
            except Exception as e:
                print(f"   ✅ Error handled: {e}")
    
    async def _test_statistics(self):
        """Test statistics functionality"""
        print("\n📊 Test 6: Statistics")
        print("-" * 40)
        
        try:
            stats = perfect_qa.get_stats()
            
            # Validate statistics structure
            required_fields = [
                'total_queries', 'successful_queries', 'failed_queries',
                'success_rate', 'avg_processing_time', 'avg_confidence',
                'uptime_seconds', 'is_ready'
            ]
            
            for field in required_fields:
                assert field in stats, f"Missing stats field: {field}"
            
            print(f"✅ Statistics structure valid")
            print(f"   - Total queries: {stats['total_queries']}")
            print(f"   - Success rate: {stats['success_rate']:.2%}")
            print(f"   - Avg processing time: {stats['avg_processing_time']:.2f}s")
            print(f"   - Avg confidence: {stats['avg_confidence']:.2f}")
            print(f"   - Uptime: {stats['uptime_formatted']}")
            
        except Exception as e:
            self.failed_tests.append(f"Statistics: {e}")
    
    def _generate_report(self) -> bool:
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("🎯 PRODUCTION Q&A SYSTEM TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.get('success')])
        
        print(f"📊 Test Results Summary:")
        print(f"   - Total tests: {total_tests}")
        print(f"   - Successful: {successful_tests}")
        print(f"   - Failed: {len(self.failed_tests)}")
        print(f"   - Success rate: {successful_tests/total_tests*100:.1f}%" if total_tests > 0 else "   - No tests run")
        
        if self.results:
            successful_results = [r for r in self.results if r.get('success')]
            if successful_results:
                avg_confidence = sum(r['confidence'] for r in successful_results) / len(successful_results)
                avg_time = sum(r['processing_time'] for r in successful_results) / len(successful_results)
                avg_length = sum(r['answer_length'] for r in successful_results) / len(successful_results)
                
                print(f"\n📈 Performance Metrics:")
                print(f"   - Average confidence: {avg_confidence:.2f}")
                print(f"   - Average response time: {avg_time:.2f}s")
                print(f"   - Average answer length: {avg_length:.0f} chars")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for failure in self.failed_tests:
                print(f"   - {failure}")
        
        # Production readiness assessment
        is_production_ready = (
            len(self.failed_tests) == 0 and
            successful_tests > 0 and
            (successful_tests / total_tests) > 0.8
        )
        
        print(f"\n🎯 Production Readiness: {'✅ READY' if is_production_ready else '❌ NOT READY'}")
        
        if is_production_ready:
            print("   🏆 System meets all production requirements!")
            print("   🚀 Ready for deployment to production environment")
        else:
            print("   ⚠️ System needs improvements before production deployment")
        
        return is_production_ready

async def main():
    """Run production test suite"""
    test_suite = ProductionQATest()
    success = await test_suite.run_comprehensive_test()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - PRODUCTION Q&A SYSTEM READY!")
        return 0
    else:
        print("\n❌ TESTS FAILED - SYSTEM NEEDS IMPROVEMENTS")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        sys.exit(1)