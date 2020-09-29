import pytest
from package.oxygen import do_utilities

class TestRhoddw:
    def test_rhoddw_1(self):
        result = do_utilities.rhoddw(temperature=20)
        assert 0.9982041322005836 == result

    def test_rhodww_2(self):
        result = do_utilities.rhoddw(temperature=5)
        assert 0.9999638212494774 == result

    def test_rhodww_3(self):
        result = do_utilities.rhoddw(temperature=28)
        assert 0.9962335095379103 == result

class TestH2odvdt1:
    def test_h2odvdt_1(self):
        result = do_utilities.h2odvdt1(vol1=300, temp1=10, temp2=20)
        assert 300.449457818352 == result

    def test_h2odvdt_2(self):
        result = do_utilities.h2odvdt1(vol1=50, temp1=15, temp2=22)
        assert 50.0666015823193 == result

    def test_h2odvdt_3(self):
        result = do_utilities.h2odvdt1(vol1=100, temp1=5, temp2=30)
        assert 100.43354334144057 == result

class TestGlassDvDt:
    def test_glassdvdt_1(self):
        result = do_utilities.glassdvdt(volume=100, known_temp=20, desired_temp=25)
        assert 100.004875 == result

    def test_glass_dvdt_2(self):
        result = do_utilities.glassdvdt(volume=500, known_temp=18, desired_temp=20)
        assert 500.00975000000005 == result

    def test_glass_dvdt_3(self):
        result = do_utilities.glassdvdt(volume=20, known_temp=18, desired_temp=22)
        assert 20.00078 == result

    def test_glass_dvdt_4(self):
        with pytest.raises(ValueError):
            do_utilities.glassdvdt(volume='f', known_temp=10, desired_temp=20)

class TestOxyCalc:
    def test_oxycalc_1(self):
        result = do_utilities.oxycalc(0.2, 1, 0.0005, 200)
        assert 5.643 == result

class TestCorrThioNorm:
    def test_corrthio_1(self):
        result = do_utilities.corrthionorm(10, 0.24, 0.0005, 0.6)
        assert 4.0033361134278564 == result

class TestGetIndex:
    def test_getindex_1(self):
        result_x = do_utilities.get_index([['column1', 'column2', 'column3'], ['data', 'data2', 'data3']], 'column3')
        assert (0, 2) == result_x

    def test_getindex_2(self):
        result_x = do_utilities.get_index([['column1', 'column2', 'column3'], ['data', 'data2', 'data3']], 'nonexist')
        assert result_x is None
