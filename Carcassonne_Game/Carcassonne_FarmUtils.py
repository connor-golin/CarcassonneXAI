from Carcassonne_Game.GameFeatures import Farm

def farmConnections(self, PlayingTile, Surroundings, MeepleUpdate, MeepleKey):
    
    for i in range(len(PlayingTile.FarmOpenings)):
        FarmOpenings = PlayingTile.FarmOpenings[i]
        AddedMeeples = self.AddMeeple(MeepleUpdate, MeepleKey, "G", i) 
        OpeningsQuantity = len(FarmOpenings)      
        if OpeningsQuantity == 1:
            oneFarmConnection(self, PlayingTile, FarmOpenings, Surroundings, AddedMeeples, i)               
        else:
            multipleFarmConnections(self, PlayingTile, FarmOpenings, OpeningsQuantity, Surroundings, AddedMeeples,i)


def oneFarmConnection(self, PlayingTile, FarmOpenings, Surroundings, AddedMeeples, i):
    FarmSide = FarmOpenings[0][0]
    FarmLine = FarmOpenings[0][1]
    if Surroundings[FarmSide] is None:
        NextFarmIndex = len(self.BoardFarms)
        self.BoardFarms[NextFarmIndex] = Farm(NextFarmIndex,AddedMeeples) #here
        self.BoardFarms[NextFarmIndex].Update([PlayingTile.TileCitiesIndex[FRCI] for FRCI in PlayingTile.FarmRelatedCityIndex[i]],[0,0])
        PlayingTile.TileFarmsIndex[FarmSide][FarmLine] = NextFarmIndex
    else:
        MatchingFarmIndex = Surroundings[FarmSide].TileFarmsIndex[self.MatchingSide[FarmSide]][self.MatchingLine[FarmLine]]
        while self.BoardFarms[MatchingFarmIndex].Pointer != self.BoardFarms[MatchingFarmIndex].ID:                            
            MatchingFarmIndex = self.BoardFarms[MatchingFarmIndex].Pointer
        MatchingFarm = self.BoardFarms[MatchingFarmIndex]
        MatchingFarm.Update([PlayingTile.TileCitiesIndex[FRCI] for FRCI in PlayingTile.FarmRelatedCityIndex[i]],AddedMeeples) 

def multipleFarmConnections(self, PlayingTile, FarmOpenings, OpeningsQuantity, Surroundings, AddedMeeples, i):
    ConnectedFarms = set()
    for (FarmSide, FarmLine) in FarmOpenings:
        if Surroundings[FarmSide] is not None:
            MatchingFarmIndex = Surroundings[FarmSide].TileFarmsIndex[self.MatchingSide[FarmSide]][self.MatchingLine[FarmLine]]
            # Find the root farm with path compression
            root_farm_index = self.find_root_farm(MatchingFarmIndex)
            ConnectedFarms.add(root_farm_index)
    if not ConnectedFarms:
        NextFarmIndex = len(self.BoardFarms)
        self.BoardFarms[NextFarmIndex] = Farm(NextFarmIndex, AddedMeeples)
        self.BoardFarms[NextFarmIndex].Update(
            [PlayingTile.TileCitiesIndex[FRCI] for FRCI in PlayingTile.FarmRelatedCityIndex[i]], [0, 0]
        )
        for (FarmSide, FarmLine) in FarmOpenings:
            PlayingTile.TileFarmsIndex[FarmSide][FarmLine] = NextFarmIndex
    else:
        CombinedFarmIndex = min(ConnectedFarms)  # Choose one root to be the combined farm
        self.BoardFarms[CombinedFarmIndex].Update(
            [PlayingTile.TileCitiesIndex[FRCI] for FRCI in PlayingTile.FarmRelatedCityIndex[i]], AddedMeeples
        )
        for root_farm_index in ConnectedFarms:
            if root_farm_index != CombinedFarmIndex:
                # Merge farms by updating pointers
                self.BoardFarms[root_farm_index].Pointer = CombinedFarmIndex
                self.BoardFarms[CombinedFarmIndex].Update(
                    self.BoardFarms[root_farm_index].CityIndexes,
                    self.BoardFarms[root_farm_index].Meeples
                )
                self.BoardFarms[root_farm_index].Meeples = [0, 0]
        for (FarmSide, FarmLine) in FarmOpenings:
            PlayingTile.TileFarmsIndex[FarmSide][FarmLine] = CombinedFarmIndex

