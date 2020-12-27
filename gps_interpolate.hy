(defn gps_interp [positions T]
    ; given two co-ordinates at given times, find GPS co-ordinates at time t
    ; (((x1,y1) t1), ((x2, y2), t2)), T
    (setv time_diff (- (get positions 1 1) (get positions 0 1)))
    (setv target_diff (- (get positions 1 1) T))
    (setv ratio (/ target_diff time_diff))
    
)