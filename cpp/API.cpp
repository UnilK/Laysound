#include<iostream>
#include<fstream>
#include<vector>
#include<array>
#include<string>
#include<cstring>
#include<algorithm>
#include<bitset>
#include<cmath>

#include"wav_parser.hpp"
#include"wav_data.hpp"

std::string merge_to_mono(
		Wave_file *file,
		Directed_wave_data *new_data
		){
	
	uint32_t data_type = (file->subformat<<16)|file->sample_size;
	uint32_t total_data_size = file->data_chunk_size/file->sample_size;

	new_data->samples_per_channel = file->data_chunk_size/file->block_align;

	new_data->audio_data[0].resize(new_data->samples_per_channel, 0);
	
	if(data_type == (uint32_t)0x00010002){
		
		// 16-bit PCM.
		int16_t *buff = new int16_t[total_data_size];
		
		if(!file->read_samples(buff, new_data->samples_per_channel)){
			return "ERROR: IMPROPERLY FORMATTED FILE";
		}
		
		for(uint32_t i=0; i<file->channel_amount; i++){
			for(uint32_t j=0; j<new_data->samples_per_channel; j++){
				new_data->audio_data[0][j] += (float)buff[i+j*file->channel_amount]/(1<<15);
			}
		}
		
		if(file->sample_rate != new_data->sample_rate){
			new_data->resample(file->sample_rate);
		}

		delete buff;

	} else if(data_type == (uint32_t)0x00030004){

		// 32-bit IEEE
		float *buff = new float[total_data_size];
		
		if(!file->read_samples(buff, new_data->samples_per_channel)){
			return "ERROR: IMPROPERLY FORMATTED FILE";
		}

		for(uint32_t i=0; i<file->channel_amount; i++){

			for(uint32_t j=0; j<new_data->samples_per_channel; j++){
				new_data->audio_data[0][j] += buff[i+j*file->channel_amount];
			}	
		}
		
		if(file->sample_rate != new_data->sample_rate){
			new_data->resample(file->sample_rate);
		}

		delete buff;

	} else {
		return "ERROR: FILE DATA TYPE NOT SUPPORTED";
	}

	return "OK";
}

std::string read_location(
		std::string file_name,
		Directed_wave_data *new_data,
		int channel
		){

	std::ifstream file_in(file_name);

	int profile_size, position_data_size, timeline_offset;
	file_in >> profile_size >> position_data_size >> timeline_offset;

	new_data->timeline_offset = timeline_offset;

	if((~new_data->channel_mask>>channel)&1){
		new_data->channel_amount++;
		new_data->damper_profile[channel].resize(256, 1);
	}
	
	new_data->channel_mask |= 1<<channel;

	if(profile_size != 0){
		if(profile_size != 256) return "ERROR: INCORRECT DAMPER PROFILE SIZE, MUST BE 0 OR 256";
		for(int i=0; i<256; i++){
			file_in >> new_data->damper_profile[channel][i];
		}
	}
	
	new_data->position_data[channel].resize(position_data_size);
	new_data->audio_data[channel].resize(position_data_size*300, 0.0);

	for(int i=0; i<position_data_size; i++){
		for(int j=0; j<3; j++){
			file_in >> new_data->position_data[channel][i][j];
		}
	}

	file_in.close();

	return "OK";
}


int main(int argc, char **argv){

	std::vector<std::string> sargv(argc);

	for(int i=0; i<argc; i++){
		sargv[i] = argv[i];
	}

	if(sargv.size() == 1) sargv.push_back("-help");

	if(sargv[1] == "-help"){

	} else if(sargv[1] == "probe" && sargv.size() > 2){
		
		std::string file_name = sargv[2];
		Wave_file file(file_name);
		std::cout << file.initialize() << '\n';
		file.file_in.close();
	
	} else if(sargv[1] == "render" && sargv.size() > 2){

		FIR_initialize();

		std::ifstream file_in(sargv[2]);
		
		int listeners_size, sources_size;
		file_in >> listeners_size >> sources_size;

		Directed_wave_data product;

		product.file_name = "renders/unnamed_project.wav";

		for(int i=3; i<(int)sargv.size(); i++){
			if(sargv[i] == "-o" && i+1 < (int)sargv.size()){
				product.file_name = sargv[i+1];
			}
		}

		for(int i=0; i<listeners_size; i++){
			
			int channel;
			std::string position_file;

			file_in >> channel >> position_file;
			
			std::cout << read_location(position_file, &product, channel) << '\n';

		}

		for(int i=0; i<sources_size; i++){
			
			std::string wave_file, position_file;

			file_in >> wave_file >> position_file;

			Wave_file audio_file(wave_file);
			Directed_wave_data audio_in = Directed_wave_data();
			std::cout << audio_file.initialize() << '\n';

			audio_in.channel_amount = 1;
			audio_in.channel_mask = 1;

			std::cout << merge_to_mono(&audio_file, &audio_in) << '\n';
			
			std::cout << read_location(position_file, &audio_in, 0) << '\n';

			product.listen(&audio_in);

		}

		std::cout << product.write_file() << '\n';

		file_in.close();
	}

}
