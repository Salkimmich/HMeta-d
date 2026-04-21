## Raw MATLAB (verbatim)

```matlab
            est_FAR2_rS2(i) = I_FAR_area_rS2 / I_area_rS2;
            est_HR2_rS2(i)  = C_HR_area_rS2 / C_area_rS2;
            
            est_FAR2_rS1(i) = I_FAR_area_rS1 / I_area_rS1;
            est_HR2_rS1(i)  = C_HR_area_rS1 / C_area_rS1;
```

```matlab
            est_FAR2_rS2(i) = I_FAR_area_rS2 / I_area_rS2;
            est_HR2_rS2(i)  = C_HR_area_rS2 / C_area_rS2;
            
            est_FAR2_rS1(i) = I_FAR_area_rS1 / I_area_rS1;
            est_HR2_rS1(i)  = C_HR_area_rS1 / C_area_rS1;
```

## Plain English gloss (line by line)

- `est_FAR2_rS2(i) = I_FAR_area_rS2 / I_area_rS2;`  
  For S2 responses at criterion index `i`, set estimated type-2 false-alarm rate to incorrect-tail area above the type-2 criterion divided by total incorrect S2-response area.
- `est_HR2_rS2(i)  = C_HR_area_rS2 / C_area_rS2;`  
  For S2 responses at criterion index `i`, set estimated type-2 hit rate to correct-tail area above the type-2 criterion divided by total correct S2-response area.
- `est_FAR2_rS1(i) = I_FAR_area_rS1 / I_area_rS1;`  
  For S1 responses at criterion index `i`, set estimated type-2 false-alarm rate to incorrect-tail area below the type-2 criterion divided by total incorrect S1-response area.
- `est_HR2_rS1(i)  = C_HR_area_rS1 / C_area_rS1;`  
  For S1 responses at criterion index `i`, set estimated type-2 hit rate to correct-tail area below the type-2 criterion divided by total correct S1-response area.
- `est_FAR2_rS2(i) = I_FAR_area_rS2 / I_area_rS2;`  
  Same computation as above, appearing in the response-conditional branch for S2 responses.
- `est_HR2_rS2(i)  = C_HR_area_rS2 / C_area_rS2;`  
  Same computation as above, appearing in the response-conditional branch for S2 responses.
- `est_FAR2_rS1(i) = I_FAR_area_rS1 / I_area_rS1;`  
  Same computation as above, appearing in the response-conditional branch for S1 responses.
- `est_HR2_rS1(i)  = C_HR_area_rS1 / C_area_rS1;`  
  Same computation as above, appearing in the response-conditional branch for S1 responses.
