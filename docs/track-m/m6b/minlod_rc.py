# Red Team M6b: M5a grid (minlod_model_m5a.py), M6a field minlod_div = B>0 and M > (count-1)*256,
# true divergence = lowest(ours) != hw (the model's own definition).
field=div=both=field_only=div_only=0; ex=[]
for B in range(0,4):
    for count in range(2,6):
        for M4 in range(1,4*(B+count-1)+1):
            M=M4*64
            ours=min(M/256.0,count-1.0)
            d=abs(max(B,ours)-max(B,M/256.0))>1e-9
            f=(B>0 and M>(count-1)*256)
            exact=(B>0 and M>256*max(B,count-1))
            field+=f; div+=d
            if f and not d:
                field_only+=1
                if len(ex)<6: ex.append((B,count,M/256.0))
            if d and not f: div_only+=1
            assert d==exact,(B,count,M)
print('grid cells field',field,'diverge',div,'field_not_diverge',field_only,'diverge_not_field',div_only)
print('examples field-only (B,count,M/256):',ex)
print('exact divergence == B>0 and M > 256*max(B,count-1): ALL OK')
